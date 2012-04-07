#!/usr/bin/env python
#

import logging
import webapp2

from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 


class ReceiveSmsHandler(webapp2.RequestHandler):
    def get(self):
        sender = self.request.get('From')
        body = self.request.get('Body')
        self.response.out.write('Received SMS from %s: %s' % (sender, body))

        # string@appid.appspotmail.com
        mail.send_mail(sender="Gateway <%s@chicago47-sms.appspotmail.com>" % sender,
              to="Chicago47 <don.schwarz@gmail.com>",
              subject="Received SMS message from %s" % sender,
              body=body)

class ReceiveEmailHandler(InboundMailHandler):
    def receive(self, message):
        logging.info("Received a message from: " + message.sender)
        bodies = message.bodies(content_type='text/plain') 
        for body in bodies: 
            logging.info("charset: %s" % body[1].charset) 
            logging.info("encoding: %s" % body[1].encoding) 
            logging.info("payload: %s" % body[1].payload) 


class ViewResponseHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('View sent SMS')


app = webapp2.WSGIApplication([('/receive-sms', ReceiveSmsHandler),
                               ('/_ah/mail/.*', ReceiveEmailHandler),
                               ('/view', ViewResponseHandler)
                               ],
                              debug=True)
