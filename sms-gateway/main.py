#!/usr/bin/env python
#

import hashlib
import logging
import os
import random
import re
import string
import webapp2

from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp import template

from twilio.rest import TwilioRestClient

# All user-specified settings go in conf.py.
import conf

EMAIL_PATTERN = re.compile(r'.*<\s*(\d+)\+([0-9a-f]+)@%s\s*>.*' % re.escape(conf.GATEWAY_DOMAIN))
REPLY_PATTERN = re.compile(r'\[REPLY BELOW THIS LINE\][\s\r\n>]*(.*?)[\s\r\n>]*\[REPLY ABOVE THIS LINE\]',
                           flags=re.MULTILINE | re.DOTALL)

class LongResponse(db.Model):
    timestamp = db.DateTimeProperty(auto_now_add=True)
    recipient = db.StringProperty()
    message = db.TextProperty()


def GetChecksum(sender):
    m = hashlib.sha1()
    m.update(sender)
    m.update(conf.CHECKSUM_KEY)
    m.update(sender)
    return m.hexdigest()

class ReceiveSmsHandler(webapp2.RequestHandler):
    def FormatEmail(self, sender, body):
        return """[REPLY BELOW THIS LINE]

[REPLY ABOVE THIS LINE]

We received the following SMS message from %s:
%s""" % (sender, body)

    def get(self):
        sender = self.request.get('From')
        body = self.request.get('Body')
        if sender[0] == '+':
            sender = sender[1:]
        sender = sender.strip()

        checksum = GetChecksum(sender)

        mail.send_mail(
            sender='%s <%s+%s@%s>' % (sender, sender, checksum, conf.GATEWAY_DOMAIN),
            to=conf.RECIPIENT,
            subject='Received SMS message from %s' % sender,
            body=self.FormatEmail(sender, body))


class ReceiveEmailHandler(InboundMailHandler):
    def ExtractSenderNumber(self, message):
        m = EMAIL_PATTERN.match(message.to)
        if m:
            sender = m.group(1)
            checksum = m.group(2)
            
            if GetChecksum(sender) != checksum:
                raise Exception('Mismatched checksum: %s vs. %s' % (checksum, GetChecksum(sender)))
                
            return sender
        else:
            raise Exception('Could not find sender in %s' % message.to)

    def GetTextBody(self, message):
        bodies = message.bodies(content_type='text/plain') 
        for body in bodies: 
            return body[1].payload

    def RemoveReply(self, text):
        m = REPLY_PATTERN.search(text)
        if m:
            return m.group(1)
        else:
            # Send bounce message.
            return None

    def receive(self, message):
        logging.info('Received a message from: ' + message.sender)
        sender = self.ExtractSenderNumber(message)
        payload = self.GetTextBody(message)

        payload = self.RemoveReply(payload)
        if payload is None or len(payload.strip()) == 0:
            mail.send_mail(
                sender='Error <noreply@%s>' % (conf.GATEWAY_DOMAIN),
                to=conf.RECIPIENT,
                subject='Received SMS message from %s' % sender,
                body="""Unable to process your response.

Be sure that you are inserting your message between the [REPLY BELOW
THIS LINE] and [REPLY ABOVE THIS LINE] markers.

Your reply was:
%s""" % self.GetTextBody(message))
            return

        client = TwilioRestClient(conf.TWILIO_ACCOUNT,
                                  conf.TWILIO_TOKEN)
        if len(payload) > conf.MAX_MESSAGE_LENGTH:
            id = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(conf.MESSAGE_ID_LENGTH))
            resp = LongResponse(key_name=id,
                                recipient=sender,
                                message=payload)
            resp.put()
            payload = payload[:conf.MAX_MESSAGE_LENGTH] + '... For more, visit http://w47.us/v/%s' % id

        payload = payload.replace('\r', '').replace('\n', ' ').strip()

        if conf.SEND_SMS_ENABLED:
            message = client.sms.messages.create(
                to='+' + sender, from_=conf.SMS_PHONE_NUMBER,
                body=payload)
        else:
            logging.info('SEND_SMS_ENABLED is False, not sending: %s' % payload)
        

class ReplyResponseHandler(webapp2.RequestHandler):
    def get(self, reply_id):
        response = LongResponse.get_by_key_name(reply_id)

        path = os.path.join(os.path.dirname(__file__), 'views', 'reply.html')
        self.response.out.write(template.render(path, {
                    'timestamp': response.timestamp.strftime('%A %B %d, %Y at %I:%M:%S %p'),
                    'message': response.message}))

        
class IndexResponseHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'views', 'index.html')
        self.response.out.write(template.render(path, {}))


app = webapp2.WSGIApplication([ReceiveEmailHandler.mapping(),
                               ('/receive-sms', ReceiveSmsHandler),
                               ('/v/(.*)', ReplyResponseHandler),
                               ('/', IndexResponseHandler),
                               ],
                              debug=True)
