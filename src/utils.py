import os
import re
from functools import wraps
from random import randint

import retrying
import sendgrid
from flask import request, Response
from sendgrid.helpers.mail import Mail, Email, Content

from src.api.api_exception import ApiException


def sanitize_label_value(value):
    regexp = r"[^A-Za-z0-9-_]"
    return re.sub(regexp, '', value).lower()


def make_project_name(name, env):
    max_len = 30
    regexp = r"[^A-Za-z0-9-! ]"
    sanitized_name = re.sub(regexp, '', name)
    # Truncate name to respect the maximum of 30 characters
    trunc_name = sanitized_name[0:max_len - len(' - ') - len(env)]
    project_name = "{name} - {env}".format(
        name=trunc_name,
        env=env,
    )
    return project_name


def make_project_id(name):
    max_len = 30
    regexp = r"[^A-Za-z]"
    prefix = os.environ.get('PROJECT_ID_PREFIX', 'c4')
    suffix = str(randint(1, 9999))
    # Truncate id to respect the maximum of 30 characters
    name = re.sub(regexp, '', name).lower()[
           0:max_len-len(prefix)-2*len('-')-len(suffix)
           ]
    project_id = '{prefix}-{name}-{suffix}'.format(
        prefix=prefix,
        name=name,
        suffix=suffix
    )
    return project_id


@retrying.retry(wait_exponential_multiplier=1000,
                wait_exponential_max=10000,
                stop_max_delay=30000)
def with_retry(request):
    return request.execute()


def validate_data(payload, schema):
    m_schema = schema()
    data, errors = m_schema.dump(payload)
    if errors:
        raise ApiException("Validation error", 400, payload=errors)

    return data


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == os.environ.get('BASIC_AUTH_USERNAME', 'front') \
           and password == os.environ.get('BASIC_AUTH_PASSWORD', 'dev')


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated




# checks if email is valid
def validate_email(user_email):
    if '@' not in user_email:
        return 0

    if len(user_email.split('@')) != 2:
        return 0

    domain = user_email.split('@')[1]



# checks if user role is correct
def validate_user_role(role):
    if role not in ["editor", "viewer", "owner"]:
        return 0


def check_if_role_exists(bindings, role):
    for binding in bindings:
        role_to_add = "roles/" + role
        if binding.get('role') == role_to_add:
            return binding
    return 0
