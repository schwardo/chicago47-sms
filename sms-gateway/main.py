#!/usr/bin/env python
#

import re
import logging
import webapp2

from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 

from twilio.rest import TwilioRestClient

# All user-specified settings go in conf.py.
import conf

class ReceiveSmsHandler(webapp2.RequestHandler):
    def get(self):
        sender = self.request.get('From')
        body = self.request.get('Body')
        if sender[0] == '+':
            sender = sender[1:]

        self.response.out.write('Received SMS from %s: %s' % (sender, body))

        # string@appid.appspotmail.com
        mail.send_mail(sender="%s <%s@%s>" % (sender, sender, GATEWAY_DOMAIN),
              to=RECIPIENT,
              subject="Received SMS message from %s" % sender,
              body=body)

class ReceiveEmailHandler(InboundMailHandler):
    def receive(self, message):
        logging.info("Received a message from: " + message.sender)
        sender = None
        for to in [message.to]:
            m = EMAIL_PATTERN.match(to)
            if m:
                sender = m.group(1)

        if not sender:
            raise Exception('Could not find sender in %s' % message.to())

        bodies = message.bodies(content_type='text/plain') 
        payload = None
        for body in bodies: 
            logging.debug("charset: %s" % body[1].charset) 
            logging.debug("encoding: %s" % body[1].encoding) 
            logging.debug("payload: %s" % body[1].payload) 
            payload = body[1].payload

        client = TwilioRestClient(TWILIO_ACCOUNT, TWILIO_TOKEN)
        if len(payload) > 155:
            payload = payload[:155] + '...'

        if SEND_SMS_ENABLED:
            message = client.sms.messages.create(
                to='+' + sender, from_=SMS_PHONE_NUMBER,
                body=payload)
        else:
            logger.info('SEND_SMS_ENABLED is False, not sending SMS.')
        

class ViewResponseHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('View sent SMS')


app = webapp2.WSGIApplication([('/receive-sms', ReceiveSmsHandler),
                               ('/_ah/mail/.*', ReceiveEmailHandler),
                               ('/view', ViewResponseHandler)
                               ],
                              debug=True)
