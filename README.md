Installation
============

Download the code and run
    python setup.py install

Usage
==========
Basic usage
    from pyc2dm import C2DM
    
    c = C2DM(email="YOUR USERNAME", password="YOUR PASSWORD", source="COMPANY.APP.VERSION")
    c.send_message("REGISTRATION_ID", "COLLAPSE KEY", {"optional":"data", "whatever": "you want"})

This can raise a number of exceptions, some are handled automatically
by retrying with exponential backoff. Others, you'll need to handle. Here's
a more complete example. You can see all the details by looking through the code.
    from pyc2dm import *
    ## Setup logging ##
    
    c = C2DM(email="YOUR USERNAME", password="YOUR PASSWORD", source="COMPANY.APP.VERSION")
    try:
        token = c.get_client_token()
    except C2DMException as e:
        raise # couldn't get a client token
    
    cache_token_for_future_use(token)
    # Then in the future use C2DM(client_token="YOUR TOKEN", source="COMPANY.APP.VERSION")
    
    try:
        c.send_notification("REGISTRATION_ID", "COLLAPSE KEY", {"optional":"data"})
    except C2DMInvalidDeviceException as e:
        remove_device("REGISTRATION_ID") ## Remove this device from your list
    except C2DMException as e:
        logger.error("Something else bad happened: %s", e)

Testing
========

To run tests, put your gmail account/password and a valid device registration id
into the test.py file, then run
    python test/test.py
