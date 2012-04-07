# -*- coding: utf-8 -*-
from mock import patch, Mock
from twilio.rest import resources

@patch("httplib2.Http")
@patch("twilio.rest.resources.Response")
def test_ascii_encode(resp_mock, mock):
    http = mock.return_value
    http.request.return_value = (Mock(), Mock())

    data = {
        "body": "HeyHey".encode('utf-8')
        }
    
    resources.make_request("GET", "http://www.example.com", data=data)

    http.request.assert_called_with("http://www.example.com", "GET", 
            headers=None, body="body=HeyHey")


@patch("httplib2.Http")
@patch("twilio.rest.resources.Response")
def test_ascii(resp_mock, mock):
    http = mock.return_value
    http.request.return_value = (Mock(), Mock())

    data = {
        "body": "HeyHey" 
        }
    
    resources.make_request("GET", "http://www.example.com", data=data)

    http.request.assert_called_with("http://www.example.com", "GET", 
            headers=None, body="body=HeyHey")


@patch("httplib2.Http")
@patch("twilio.rest.resources.Response")
def test_double_encoding(resp_mock, mock):
    http = mock.return_value
    http.request.return_value = (Mock(), Mock())

    body = u"Chloéñ"

    data = {
        "body": body.encode('utf-8'),
        }
    
    resources.make_request("GET", "http://www.example.com", data=data)

    http.request.assert_called_with("http://www.example.com", "GET", 
            headers=None, body="body=Chlo%C3%A9%C3%B1")


@patch("httplib2.Http")
@patch("twilio.rest.resources.Response")
def test_paging(resp_mock, mock):
    http = mock.return_value
    http.request.return_value = (Mock(), Mock())

    data = {
        "body": u"Chloéñ",
        }
    
    resources.make_request("GET", "http://www.example.com", data=data)

    http.request.assert_called_with("http://www.example.com", "GET", 
            headers=None, body="body=Chlo%C3%A9%C3%B1")



