"""An example config.py file."""
import ee
from flask import current_app

# The URL of the Earth Engine API.
EE_URL = 'https://earthengine.googleapis.com'

# The service account email address authorized by your Google contact.
# Set up a service account as described here:
EE_ACCOUNT = ''.join([
    current_app.config['EE_CLIENT_ID'],
    '@developer.gserviceaccount.com'
])

# The private key associated with your service account in Privacy Enhanced
# Email format (.pem suffix).  To convert a private key from the RSA format
# (.p12 suffix) to .pem, run the openssl command like this:
# openssl pkcs12 -in downloaded-privatekey.p12 -nodes -nocerts > privatekey.pem
EE_PRIVATE_KEY_FILE = 'privatekey.pem'

# DEBUG_MODE will be True if running in a local development environment.
# DEBUG_MODE = ('SERVER_SOFTWARE' in os.environ and
#              os.environ['SERVER_SOFTWARE'].startswith('Dev'))
EE_CREDENTIALS = ee.ServiceAccountCredentials(
    EE_ACCOUNT,
    EE_PRIVATE_KEY_FILE
)
