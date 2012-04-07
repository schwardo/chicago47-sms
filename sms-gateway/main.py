#!/usr/bin/env python
#
import webapp2

from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 


class ReceiveSmsHandler(webapp2.RequestHandler):
    def get(self):
        sender = self.request.get('From')
        body = self.request.get('Body')
        self.response.out.write('Received SMS from %s: %s' % (sender, body))

        # string@appid.appspotmail.com
        mail.send_mail(sender="Gateway <%s@chicago47-sms.appspotmail.com" % sender,
              to="Chicago47 <don.schwarz@gmail.com>",
              subject="Received SMS message from %s" % sender,
              body=body)

class ReceiveEmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        logging.info('\n'.join(message.bodies('text/plain')))


class ViewResponseHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('View sent SMS')


app = webapp2.WSGIApplication([('/receive-sms', ReceiveSmsHandler),
                               ('/_ah/mail/.*', ReceiveEmailHandler),
                               ('/view', ViewResponseHandler)
                               ],
                              debug=True)
