"""
Make sure to check out the TwiML overview and tutorial
"""

import xml.etree.ElementTree as ET


class TwimlException(Exception):
    pass


class Verb(object):
    """Twilio basic verb object.
    """
    GET = "GET"
    POST = "POST"
    nestables = None

    def __init__(self, **kwargs):
        self.name = self.__class__.__name__
        self.body = None
        self.verbs = []
        self.attrs = {}

        if kwargs.get("waitMethod", "GET") not in ["GET", "POST"]:
            raise TwimlException("Invalid waitMethod parameter, "
                                 "must be 'GET' or 'POST'")

        if kwargs.get("method", "GET") not in ["GET", "POST"]:
            raise TwimlException("Invalid method parameter, "
                                 "must be 'GET' or 'POST'")

        for k, v in kwargs.items():
            if k == "sender":
                k = "from"
            if v is not None:
                self.attrs[k] = v

    def __str__(self):
        return self.toxml()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def toxml(self, xml_declaration=True):
        """
        Return the contents of this verb as an XML string

        :param bool xml_declaration: Include the XML declaration. Defaults to
                                     True
        """
        xml = ET.tostring(self.xml()).encode("utf-8")

        if xml_declaration:
            return u'<?xml version="1.0" encoding="UTF-8"?>' + xml
        else:
            return xml

    def xml(self):
        el = ET.Element(self.name)

        keys = self.attrs.keys()
        keys.sort()
        for a in keys:
            value = self.attrs[a]

            if isinstance(value, bool):
                el.set(a, str(value).lower())
            else:
                el.set(a, str(value))

        if self.body:
            el.text = self.body

        for verb in self.verbs:
            el.append(verb.xml())

        return el

    def append(self, verb):
        print self.nestables
        if not self.nestables or verb.name not in self.nestables:
            raise TwimlException("%s is not nestable inside %s" % \
                (verb.name, self.name))
        self.verbs.append(verb)
        return verb


class Response(Verb):
    """Twilio response object."""
    nestables = [
        'Say',
        'Play',
        'Gather',
        'Record',
        'Dial',
        'Redirect',
        'Pause',
        'Hangup',
        'Reject',
        'Sms',
        ]

    def __init__(self, **kwargs):
        """Version: Twilio API version e.g. 2008-08-01 """
        super(Response, self).__init__(**kwargs)

    def say(self, text, **kwargs):
        """Return a newly created :class:`Say` verb, nested inside this
        :class:`Response` """
        return self.append(Say(text, **kwargs))

    def play(self, url, **kwargs):
        """Return a newly created :class:`Play` verb, nested inside this
        :class:`Response` """
        return self.append(Play(url, **kwargs))

    def pause(self, **kwargs):
        """Return a newly created :class:`Pause` verb, nested inside this
        :class:`Response` """
        return self.append(Pause(**kwargs))

    def redirect(self, url=None, **kwargs):
        """Return a newly created :class:`Redirect` verb, nested inside this
        :class:`Response` """
        return self.append(Redirect(url, **kwargs))

    def hangup(self, **kwargs):
        """Return a newly created :class:`Hangup` verb, nested inside this
        :class:`Response` """
        return self.append(Hangup(**kwargs))

    def reject(self, reason=None, **kwargs):
        """Return a newly created :class:`Hangup` verb, nested inside this
        :class:`Response` """
        return self.append(Reject(reason=reason, **kwargs))

    def gather(self, **kwargs):
        """Return a newly created :class:`Gather` verb, nested inside this
        :class:`Response` """
        return self.append(Gather(**kwargs))

    def dial(self, number=None, **kwargs):
        """Return a newly created :class:`Dial` verb, nested inside this
        :class:`Response` """
        return self.append(Dial(number, **kwargs))

    def record(self, **kwargs):
        """Return a newly created :class:`Record` verb, nested inside this
        :class:`Response` """
        return self.append(Record(**kwargs))

    def sms(self, msg, **kwargs):
        """Return a newly created :class:`Sms` verb, nested inside this
        :class:`Response` """
        return self.append(Sms(msg, **kwargs))

    # All add* methods are deprecated
    def addSay(self, *args, **kwargs):
        return self.say(*args, **kwargs)

    def addPlay(self, *args, **kwargs):
        return self.play(*args, **kwargs)

    def addPause(self, *args, **kwargs):
        return self.pause(*args, **kwargs)

    def addRedirect(self, *args, **kwargs):
        return self.redirect(*args, **kwargs)

    def addHangup(self, *args, **kwargs):
        return self.hangup(*args, **kwargs)

    def addReject(self, *args, **kwargs):
        return self.reject(*args, **kwargs)

    def addGather(self, *args, **kwargs):
        return self.gather(*args, **kwargs)

    def addDial(self, *args, **kwargs):
        return self.dial(*args, **kwargs)

    def addRecord(self, *args, **kwargs):
        return self.record(*args, **kwargs)

    def addSms(self, *args, **kwargs):
        return self.sms(*args, **kwargs)


class Say(Verb):
    """The :class:`Say` verb converts text to speech that is read back to the
    caller.

    :param voice: allows you to choose a male or female voice to read text
                  back.

    :param language: allows you pick a voice with a specific language's accent
                     and pronunciations. Twilio currently supports languages
                     'en' (English), 'es' (Spanish), 'fr' (French), and 'de'
                     (German), 'en-gb' (English Great Britain").

    :param loop: specifies how many times you'd like the text repeated.
                 Specifying '0' will cause the the :class:`Say` verb to loop
                 until the call is hung up.
    """
    MAN = 'man'
    WOMAN = 'woman'

    ENGLISH = 'en'
    BRITISH = 'en-gb'
    SPANISH = 'es'
    FRENCH = 'fr'
    GERMAN = 'de'

    def __init__(self, text, **kwargs):
        super(Say, self).__init__(**kwargs)
        self.body = text


class Play(Verb):
    """Play an audio file at a URL

    :param url: point to af audio file. The MIME type on the file must be set
                correctly.

    :param loop: specifies how many times you'd like the text repeated.
                 Specifying '0' will cause the the :class:`Say` verb to loop
                 until the call is hung up. Defaults to 1.
    """
    def __init__(self, url, **kwargs):
        super(Play, self).__init__(**kwargs)
        self.body = url


class Pause(Verb):
    """Pause the call

    :param length: specifies how many seconds Twilio will wait silently before
                   continuing on.
    """


class Redirect(Verb):
    """Redirect call flow to another URL

    :param url: specifies the url which Twilio should query to retrieve new
                TwiML. The default is the current url

    :param method: specifies the HTTP method to use when retrieving the url
    """
    GET = 'GET'
    POST = 'POST'

    def __init__(self, url="", **kwargs):
        super(Redirect, self).__init__(**kwargs)
        self.body = url


class Hangup(Verb):
    """Hangup the call
    """


class Reject(Verb):
    """Hangup the call

    :param reason: not sure
    """


class Gather(Verb):
    """Gather digits from the caller's keypad

    :param action: URL to which the digits entered will be sent
    :param method: submit to 'action' url using GET or POST
    :param numDigits: how many digits to gather before returning
    :param timeout: wait for this many seconds before returning
    :param finishOnKey: key that triggers the end of caller input
    """
    GET = 'GET'
    POST = 'POST'
    nestables = ['Say', 'Play', 'Pause']

    def __init__(self, **kwargs):
        super(Gather, self).__init__(**kwargs)

    def say(self, text, **kwargs):
        return self.append(Say(text, **kwargs))

    def play(self, url, **kwargs):
        return self.append(Play(url, **kwargs))

    def pause(self, **kwargs):
        return self.append(Pause(**kwargs))

    def addSay(self, *args, **kwargs):
        return self.say(*args, **kwargs)

    def addPlay(self, *args, **kwargs):
        return self.play(*args, **kwargs)

    def addPause(self, *args, **kwargs):
        return self.pause(*args, **kwargs)


class Number(Verb):
    """Specify phone number in a nested Dial element.

    :param number: phone number to dial
    :param sendDigits: key to press after connecting to the number
    """
    def __init__(self, number, **kwargs):
        super(Number, self).__init__(**kwargs)
        self.body = number


class Client(Verb):
    """Specify a client name to call in a nested Dial element.

    :param name: Client name to connect to
    """
    def __init__(self, name, **kwargs):
        super(Client, self).__init__(**kwargs)
        self.body = name


class Sms(Verb):
    """ Send a Sms Message to a phone number

    :param to: whom to send message to
    :param sender: whom to send message from.
    :param action: url to request after the message is queued
    :param method: submit to 'action' url using GET or POST
    :param statusCallback: url to hit when the message is actually sent
    """
    GET = 'GET'
    POST = 'POST'

    def __init__(self, msg, **kwargs):
        super(Sms, self).__init__(**kwargs)
        self.body = msg


class Conference(Verb):
    """Specify conference in a nested Dial element.

    :param name: friendly name of conference
    :param bool muted: keep this participant muted
    :param bool beep: play a beep when this participant enters/leaves
    :param bool startConferenceOnEnter: start conf when this participants joins
    :param bool endConferenceOnExit: end conf when this participants leaves
    :param waitUrl: TwiML url that executes before conference starts
    :param waitMethod: HTTP method for waitUrl GET/POST
    """
    GET = 'GET'
    POST = 'POST'

    def __init__(self, name, **kwargs):
        super(Conference, self).__init__(**kwargs)
        self.body = name


class Dial(Verb):
    """Dial another phone number and connect it to this call

    :param action: submit the result of the dial to this URL
    :param method: submit to 'action' url using GET or POST
    :param int timeout: The number of seconds to waits for the called 
                         party to answer the call
    :param bool hangupOnStar: Allow the calling party to hang up on the 
                              called party by pressing the '*' key
    :param int timeLimit: The maximum duration of the Call in seconds
    :param callerId: The caller ID that will appear to the called party
    :param bool record: Record both legs of a call within this <Dial>
    """
    GET = 'GET'
    POST = 'POST'
    nestables = ['Number', 'Conference', 'Client']

    def __init__(self, number=None, **kwargs):
        super(Dial, self).__init__(**kwargs) 
        if number and len(number.split(',')) > 1:
            for n in number.split(','):
                self.append(Number(n.strip()))
        else:
            self.body = number

    def client(self, name, **kwargs):
        return self.append(Client(name, **kwargs))

    def number(self, number, **kwargs):
        return self.append(Number(number, **kwargs))

    def conference(self, name, **kwargs):
        return self.append(Conference(name, **kwargs))

    def addNumber(self, *args, **kwargs):
        return self.number(*args, **kwargs)

    def addConference(self, *args, **kwargs):
        return self.conference(*args, **kwargs)


class Record(Verb):
    """Record audio from caller

    :param action: submit the result of the dial to this URL
    :param method: submit to 'action' url using GET or POST
    :param maxLength: maximum number of seconds to record
    :param timeout: seconds of silence before considering the recording done
    """
    GET = 'GET'
    POST = 'POST'
