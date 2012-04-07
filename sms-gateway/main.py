#!/usr/bin/env python
#

import re
import logging
import os
import webapp2

from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp import template

from twilio.rest import TwilioRestClient

# All user-specified settings go in conf.py.
import conf

EMAIL_PATTERN = re.compile(r'.*<\s*(\d+)@%s\s*>.*' % re.escape(conf.GATEWAY_DOMAIN))
REPLY_PATTERN = re.compile(r'\[REPLY BELOW THIS LINE\][\s\r\n>]*(.*?)[\s\r\n>]*\[REPLY ABOVE THIS LINE\]',
                           flags=re.MULTILINE)

class ReceiveSmsHandler(webapp2.RequestHandler):
    def get(self):
        sender = self.request.get('From')
        body = self.request.get('Body')
        if sender[0] == '+':
            sender = sender[1:]

        self.response.out.write('Received SMS from %s: %s' % (sender, body))

        mail.send_mail(sender="%s <%s@%s>" % (sender, sender, conf.GATEWAY_DOMAIN),
              to=conf.RECIPIENT,
              subject="Received SMS message from %s" % sender,
              body='[REPLY BELOW THIS LINE]\n\n[REPLY ABOVE THIS LINE]\n\n' + body)

class ReceiveEmailHandler(InboundMailHandler):
    def ExtractSenderNumber(self, message):
        logging.info('Email was sent to: %r' % message.to)
        m = EMAIL_PATTERN.match(message.to)
        if m:
            return m.group(1)
        else:
            raise Exception('Could not find sender in %s' % message.to)

    def GetTextBody(self, message):
        bodies = message.bodies(content_type='text/plain') 
        for body in bodies: 
            logging.debug("charset: %s" % body[1].charset) 
            logging.debug("encoding: %s" % body[1].encoding) 
            logging.debug("payload: %s" % body[1].payload) 
            return body[1].payload

    def RemoveReply(self, text):
        # TODO: strip out quoted reply from text
        m = REPLY_PATTERN.search(text)
        if m:
            return m.group(1)
        else:
            return None

    def receive(self, message):
        logging.info("Received a message from: " + message.sender)
        sender = self.ExtractSenderNumber(message)
        payload = self.GetTextBody(message)

        payload = self.RemoveReply(payload)
        if payload is None:
            logging.info('Could not find reply.  Ignoring.')
            return

        client = TwilioRestClient(conf.TWILIO_ACCOUNT,
                                  conf.TWILIO_TOKEN)
        if len(payload) > 155:
            payload = payload[:155] + '...'

        if conf.SEND_SMS_ENABLED:
            message = client.sms.messages.create(
                to='+' + sender, from_=conf.SMS_PHONE_NUMBER,
                body=payload)
        else:
            logging.info('SEND_SMS_ENABLED is False, not sending: %s' % payload)
        

class ReplyResponseHandler(webapp2.RequestHandler):
    def get(self, reply_id):
        path = os.path.join(os.path.dirname(__file__), 'views', 'reply.html')
        self.response.out.write(template.render(path, {}))

        
class IndexResponseHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'views', 'index.html')
        self.response.out.write(template.render(path, {}))


app = webapp2.WSGIApplication([ReceiveEmailHandler.mapping(),
                               ('/receive-sms', ReceiveSmsHandler),
                               ('/view/(.*)', ReplyResponseHandler),
                               ('/', IndexResponseHandler),
                               ],
                              debug=True)
