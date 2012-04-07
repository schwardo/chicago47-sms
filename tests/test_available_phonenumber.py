from __future__ import with_statement
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
from mock import Mock
from twilio import TwilioException
from twilio.rest.resources import AvailablePhoneNumber
from twilio.rest.resources import AvailablePhoneNumbers
from twilio.rest.resources import PhoneNumbers


class AvailablePhoneNumberTest(unittest.TestCase):

    def setUp(self):
        self.parent = Mock()
        self.instance = AvailablePhoneNumber(self.parent)

    def test_init(self):
        self.assertEquals(self.instance.name, "")

    def test_purchase(self):
        self.instance.phone_number = "+123"
        self.instance.purchase(voice_url="http://www.google.com")

        self.parent.purchase.assert_called_with(
            voice_url="http://www.google.com",
            phone_number="+123")


class AvailabePhoneNumbersTest(unittest.TestCase):

    def setUp(self):
        self.resource = AvailablePhoneNumbers("http://api.twilio.com",
                                              ("user", "pass"), Mock())

    def test_get(self):
        with self.assertRaises(TwilioException):
            self.resource.get("PN123")

    def test_list(self):
        request = Mock()
        request.return_value = (Mock(), {"available_phone_numbers": []})
        self.resource.request = request

        self.resource.list()

        uri = "http://api.twilio.com/AvailablePhoneNumbers/US/Local"
        request.assert_called_with("GET", uri, params={})

    def test_load_instance(self):
        instance = self.resource.load_instance({"hey": "you"})
        self.assertIsInstance(instance.parent, Mock)
        self.assertEquals(instance.hey, "you")

    def test_purchase_status_callback(self):
        request = Mock()
        request.return_value = (Mock(), {"available_phone_numbers": []})
        self.resource.request = request

        self.resource.list()

        uri = "http://api.twilio.com/AvailablePhoneNumbers/US/Local"
        request.assert_called_with("GET", uri, params={})


class PhoneNumbersTest(unittest.TestCase):

    def setUp(self):
        self.resource = PhoneNumbers("http://api.twilio.com",
                                     ("user", "pass"))

    def test_reference(self):
        self.assertEquals(self.resource.available_phone_numbers.phone_numbers,
                          self.resource)

    def test_purchase_status_callback(self):
        request = Mock()
        response = Mock()
        response.status_code = 201
        request.return_value = (response, {"sid": ""})
        self.resource.request = request

        self.resource.purchase(area_code="530", status_callback_url="http://",
                               status_callback_method="POST")

        uri = "http://api.twilio.com/IncomingPhoneNumbers"

        data = {
            "AreaCode": "530",
            "StatusCallback": "http://",
            "StatusCallbackMethod": "POST",
            }

        request.assert_called_with("POST", uri, data=data)
