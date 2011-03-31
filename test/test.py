import unittest

from pyc2dm import *

CLIENT_USERNAME = "youremail@gmail.com"
CLIENT_PASSWORD = "yourpass"

PHONE_REG_ID = "valid phone registration_id"

class C2DMTest(unittest.TestCase):
    """Unit tests for C2DM class."""

    def test_create(self):
        """Tests creating a C2DM"""
        try:
            C2DM()
            self.fail()
        except C2DMCredentialException as e:
            self.assertEqual(str(e), "Must give client_token or email and password")
        try:
            C2DM(client_token="asdf")
            self.fail()
        except C2DMCredentialException as e:
            self.assertEqual(str(e), "Must provide a source")
        try:
            C2DM(client_token="asdf")
            self.fail()
        except C2DMCredentialException as e:
            self.assertEqual(str(e), "Must provide a source")

    def test_get_client_token_errors(self):
        c = C2DM(email=CLIENT_USERNAME, password="wrong password I'm assuming",
                    source="appfirst.test.1")
        try:
            c.get_client_token()
        except C2DMClientTokenException as e:
            self.assertEqual(str(e).strip(), "Error=BadAuthentication")
        orig_server = C2DM.CLIENT_AUTH_TOKEN_SERVER
        C2DM.CLIENT_AUTH_TOKEN_SERVER = "https://this-isnt-a-website-404-error-afuheriuhasdkjfhasdfgl.com"
        try:
            c.get_client_token()
        except C2DMConnectionException as e:
            self.assertEqual(str(e), "Couldn't connect to Google: [Errno 8] nodename nor servname provided, or not known")
        C2DM.CLIENT_AUTH_TOKEN_SERVER = "https://google.com"
        try:
            c.get_client_token()
        except C2DMConnectionException as e:
            self.assertEqual(str(e), "Invalid response: <!doctype html><html><head><meta http-equiv=\"content-type\" conte")
        C2DM.CLIENT_AUTH_TOKEN_SERVER = orig_server
        
    def test_get_client_token(self):
        c = C2DM(email=CLIENT_USERNAME, password=CLIENT_PASSWORD, source="appfirst.test.1")
        token = c.get_client_token()
        self.assertEqual(len(token), 246)

    def test_send_message(self):
        c = C2DM(email=CLIENT_USERNAME, password=CLIENT_PASSWORD, source="appfirst.test.1")
        token = c.get_client_token()
        # Test using token directly
        c = C2DM(client_token=token, source="appfirst.test.1")
        
        # Test broken
        good_token = c.get_client_token()
        c._client_token = "bad token"
        try:
            c.send_notification("INVALID DEVICE ID", "collapsekey")
            self.fail()
        except C2DMClientTokenException as e:
            self.assertEqual(str(e), "Invalid Client Token: bad token")
        c._client_token = good_token
        try:
            c.send_notification("INVALID DEVICE ID", "collapsekey")
            self.fail()
        except C2DMInvalidDeviceException as e:
            self.assertEqual(str(e), "InvalidRegistration")
        try:
            c.send_notification(PHONE_REG_ID, "collapsekey", {"somekey":"data that is way to big"*100})
            self.fail()
        except C2DMMessageTooBigException as e:
            self.assertEqual(str(e), "")
        
        # Test working
        mid = c.send_notification(PHONE_REG_ID, "collapsekey", {"somekey":"some value here"})
        self.assertTrue(mid)

        # Should test exponential backoff


if __name__ == '__main__':
    unittest.main()
