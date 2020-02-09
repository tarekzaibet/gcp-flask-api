import os

from oauth2client import client
from src.services.storage import get_content_to_file


def datafile(filename):
    return os.path.join(CREDENTIALS_DIR, filename)


# Store OAuth2Credentials object associated with a auth_code
cached_users = {}

CREDENTIALS_DIR = "/tmp"
# Set path to the Web application client_secret_*.json file you downloaded from the
CLIENT_SECRET_FILE = datafile('client_secret_creation_form.json')


def extract_auth_code(request):
    # if not request.headers.get('X-Requested-With'):
    #     abort(403)
    try:
        # Get auth_code from custom header
        auth_code = request.headers.get('X-Auth-Code')
        print('OAUTH2 auth_code ({}): {}'.format(type(auth_code), auth_code))
        return auth_code
    except:
        print('error finding auth code in custom header')

    return '401'


def authenticate_using_auth_code(auth_code):
    credentials = credentials_using_auth_code(auth_code)

    return credentials.get_access_token()[0]


def credentials_using_auth_code(auth_code, scopes=None):
    if scopes is None:
        scopes = [
            'https://www.googleapis.com/auth/cloud-platform',
            'profile',
            'email',
            'https://www.googleapis.com/auth/admin.directory.group'
        ]

    # Fetch token from cached users
    cached_user_credentials = cached_users.get(auth_code, None)

    if cached_user_credentials is None:
        get_content_to_file("gcp-flask-api", "client_secret_creation_form.json")
        # Exchange auth code for access token, refresh token, and ID token
        credentials = client.credentials_from_clientsecrets_and_code(
            CLIENT_SECRET_FILE,
            scopes,
            auth_code)

        # Cache new user's token
        cached_users[auth_code] = credentials

    else:
        print('Returned from cached_user_credentials: {}'.format(
            cached_user_credentials))
        credentials = cached_user_credentials

    return credentials
