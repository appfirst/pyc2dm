import urllib
import urllib2
import time

__all__ = [
    'C2DM',
    'C2DMException',
    'C2DMCredentialException',
    'C2DMClientTokenException',
    'C2DMMaxAttemptsException',
    'C2DMConnectionException',
    'C2DMInvalidDeviceException',
    'C2DMMessageTooBigException',
    'C2DConnectionException'
]

class C2DMException(Exception): pass
class C2DMCredentialException(C2DMException): pass
class C2DMClientTokenException(C2DMException): pass
class C2DMMaxAttemptsException(C2DMException): pass
class C2DMConnectionException(C2DMException): pass
class C2DMInvalidDeviceException(C2DMException): pass
class C2DMMessageTooBigException(C2DMException): pass
class C2DConnectionException(C2DMException): pass


class C2DM(object):
    """Client for C2DM connection. Used to send push notifications to
    Android phones."""

    CLIENT_AUTH_TOKEN_SERVER = "https://www.google.com/accounts/ClientLogin"
    C2DM_API_SERVER = "https://android.apis.google.com/c2dm/send"

    def __init__(self, email=None, password=None, client_token=None, source=None,
        max_attempts=5):
        """
        Create a C2DM connection manager. You must include a client_token or
        an email and password. If you give a client_token that is used, otherwise
        it attempts to get your client_token from the email/password. This can
        fail (or require a captcha) if repeated too many times, so just use
        it the first time, and then pass your client_token, which you can get with:

        >>> c = C2DM(email="YOUR EMAIL", password="YOUR PASSWORD", source="APPLICATION NAME")
        >>> c.get_client_token()
        YOUR CLIENT TOKEN HERE

        :param email: Your email. Only used if client_token not given.
        :param password: Your password. Only used if client_token not given.
        :param client_token: Your client token.
        :param source: Your application name, usually like "companyName-appName-versionID".
        :param max_attempts: The max number of tries to attempt sending requets,
            using exponential backoff (so a value of 5 can take up to 0+1+2+4+8 = 15 seconds),
            so it will take at most 2**(n-1)-1 seconds.
        :raises C2DMCredentialException: If you don't give source and client_token or email/password.
        """
        super(C2DM, self).__init__()
        self._account_type = "HOSTED_OR_GOOGLE"
        self._email = email
        self._password = password
        self._client_token = client_token
        self._source = source
        self._max_attempts = max_attempts
        if not client_token and not (email and password):
            raise C2DMCredentialException("Must give client_token or email and password")
        if not source:
            raise C2DMCredentialException("Must provide a source")

    def get_client_token(self):
        """Gets this applications client token. Caches the value so we only
        request it once in the lifetime of this C2DM object.

        :raises C2DMClientTokenException: If there is a problem retrieving the token,
            like a captcha is required.
        """
        if not self._client_token:
            self._init_client_token()
        return self._client_token

    def _init_client_token(self):
        args = {
            "accountType": self._account_type,
            "Email": self._email,
            "Passwd": self._password,
            "service": "ac2dm",
            "source": self._source,
        }
        data = urllib.urlencode(args)
        request = urllib2.Request(C2DM.CLIENT_AUTH_TOKEN_SERVER, data)
        try:
            response = urllib2.urlopen(request).read()
        except urllib2.HTTPError as e:
            raise C2DMClientTokenException(e.read())
        except urllib2.URLError as e:
            raise C2DMConnectionException("Couldn't connect to Google: %s" % e.reason)
        try:
            responseAsList = response.strip().split('\n')
            self._client_token = responseAsList[2].split('=')[1]
        except Exception, e:
            raise C2DMConnectionException("Invalid response: %s" % response[:64])

    def send_notification(self, device_id, collapse_key, data={}):
        """Sends a push notification to a device.

        :return: The message id.
        :rtype: String.

        :raises C2DMClientTokenException: If there is a problem retrieving or using the token,
            like a captcha is required or it's an invalid token.
        :raises C2DMMaxAttemptsException: If it can't send the message in the max number of attempts.
        :raises C2DMConnectionException: Generic problem that isn't one of the others.
            Content will include a description of the problem.
        :raises C2DMInvalidDeviceException: The given device is invalid. Stop sending messages to it!
        :raises C2DMMessageTooBigException: The message you are sending is too large, 1024 bytes max.
        """
        args = {
            "registration_id": device_id,
            "collapse_key": collapse_key,
        }
        for k, v in data.iteritems():
            args["data.%s" % k] = v
        headers = {'Authorization': 'GoogleLogin auth=' + self.get_client_token()}
        data = urllib.urlencode(args)
        request = urllib2.Request(C2DM.C2DM_API_SERVER, data, headers)
        return self._make_push_request(request)

    def _make_push_request(self, request, attempt=1):
        if attempt > self._max_attempts:
            raise C2DMMaxAttemptsException("Failed after %s tries" % (attempt-1))
        try:
            response = urllib2.urlopen(request).read()
        except urllib2.HTTPError as e:
            if e.code == 401:
                raise C2DMClientTokenException("Invalid Client Token: %s" % self._client_token)
            if e.code == 503:
                wait_time = int(e.hdrs.get('Retry-After', 0))
                if not wait_time:
                    wait_time = 2**(attempt-1)
                time.sleep(wait_time)
                return self._make_push_request(request, attempt+1)
            raise C2DMConnectionException("Unknown exception sending notification, status code: %s" % e.code)
        except urllib2.URLError as e:
            raise C2DMConnectionException("Couldn't connect to Google: %s" % e.reason)

        try:
            key, val = response.strip().split("=")
        except Exception:
            raise C2DConnectionException("Unknown response received: %s" % response)
        if key == "id":
            return val
        if val in ["InvalidRegistration", "NotRegistered"]:
            raise C2DMInvalidDeviceException(val)
        if val in ["MessageTooBig"]:
            raise C2DMMessageTooBigException()
        if val in ["QuotaExceeded", "DeviceQuotaExceeded"]:
            time.sleep(2**(attempt-1))
            return self._make_push_request(request, attempt+1)

        raise C2DConnectionException("Unknown response received: %s" % response)
