import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
from mock import Mock
from twilio import TwilioException
from twilio.rest.resources import Application
from twilio.rest.resources import Applications


class ApplicationsTest(unittest.TestCase):

    def setUp(self):
        self.parent = Mock()
        self.resource = Applications("http://api.twilio.com", ("user", "pass"))

    def test_create_appliation_sms_url_method(self):
        self.resource.create_instance = Mock()
        self.resource.create(sms_method="hey")
        self.resource.create_instance.assert_called_with({"SmsMethod": "hey"})

    def test_create_appliation_sms_url(self):
        self.resource.create_instance = Mock()
        self.resource.create(sms_url="hey")
        self.resource.create_instance.assert_called_with({"SmsUrl": "hey"})

    def test_update_appliation_sms_url_method(self):
        self.resource.update_instance = Mock()
        self.resource.update("123", sms_method="hey")
        self.resource.update_instance.assert_called_with(
            "123", {"SmsMethod": "hey"})

    def test_update_appliation_sms_url(self):
        self.resource.update_instance = Mock()
        self.resource.update("123", sms_url="hey")
        self.resource.update_instance.assert_called_with(
            "123", {"SmsUrl": "hey"})

    def test_update(self):
        request = Mock()
        request.return_value = (Mock(), {"sid": "123"})
        self.resource.request = request

        self.resource.update("123", voice_url="hey")

        uri = "http://api.twilio.com/Applications/123"
        request.assert_called_with("POST", uri, data={"VoiceUrl":"hey"})

    def test_create(self):
        request = Mock()
        request.return_value = (request, {"sid": "123"})
        request.status_code = 201

        self.resource.request = request

        self.resource.create(friendly_name="hey")

        uri = "http://api.twilio.com/Applications"
        request.assert_called_with("POST", uri, data={"FriendlyName":"hey"})
