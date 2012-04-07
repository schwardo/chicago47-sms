# twilio-python

[![Build Status](https://secure.travis-ci.org/twilio/twilio-python.png?branch=master)](http://travis-ci.org/twilio/twilio-python)

A module for using the Twilio REST API and generating valid
[TwiML](http://www.twilio.com/docs/api/twiml/ "TwiML -
Twilio Markup Language"). [Click here to read the full
documentation.](http://readthedocs.org/docs/twilio-python/en/latest/ "Twilio
Python library documentation")

## Installation

Install from PyPi using [pip](http://www.pip-installer.org/en/latest/), a
package manager for Python.

    $ pip install twilio

Don't have pip installed? Try installing it, by running this from the command
line:

    $ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python

Or, you can [download the source code
(ZIP)](https://github.com/twilio/twilio-python/zipball/master "twilio-python
source code") for `twilio-python`, and then run:

    $ python setup.py install

You may need to run the above commands with `sudo`.

## Getting Started

Getting started with the Twilio API couldn't be easier. Create a
`TwilioRestClient` and you're ready to go.

### API Credentials

The `TwilioRestClient` needs your Twilio credentials. You can either pass these
directly to the constructor (see the code below) or via environment variables.

```python
from twilio.rest import TwilioRestClient

account = "ACXXXXXXXXXXXXXXXXX"
token = "YYYYYYYYYYYYYYYYYY"
client = TwilioRestClient(account, token)
```

Alternately, a `TwilioRestClient` constructor without these parameters will
look for `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` variables inside the
current environment.

We suggest storing your credentials as environment variables. Why? You'll never
have to worry about committing your credentials and accidentally posting them
somewhere public.


```python
from twilio.rest import TwilioRestClient
client = TwilioRestClient()
```

### Make a Call

```python
from twilio.rest import TwilioRestClient

account = "ACXXXXXXXXXXXXXXXXX"
token = "YYYYYYYYYYYYYYYYYY"
client = TwilioRestClient(account, token)

call = client.calls.create(to="9991231234", 
                           from_="9991231234", 
                           url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient")
print call.sid
```

### Send an SMS
```python
from twilio.rest import TwilioRestClient

account = "ACXXXXXXXXXXXXXXXXX"
token = "YYYYYYYYYYYYYYYYYY"
client = TwilioRestClient(account, token)

message = client.sms.messages.create(to="+12316851234", from_="+15555555555",
                                     body="Hello there!")
```

### Handling a call using TwiML

To control phone calls, your application needs to output
[TwiML](http://www.twilio.com/docs/api/twiml/ "TwiML - Twilio Markup
Language"). Use `twilio.twiml.Response` to easily create such responses.

```python
from twilio import twiml

r = twiml.Response()
r.say("Welcome to twilio!")
print str(r)
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<Response><Say>Welcome to twilio!</Say></Response>
```

### Digging Deeper

The full power of the Twilio API is at your fingertips. The [full
documentation](http://readthedocs.org/docs/twilio-python/en/latest/ "Twilio
Python library documentation") explains all the awesome features available to
use.
