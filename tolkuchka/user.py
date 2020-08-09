import time

import six
from jwt import jwt, PyJWTError
from werkzeug.exceptions import Unauthorized

JWT_ISSUER = 'com.tolkuchka.app'
JWT_SECRET = 'adf85hgpe8Chrvhg2wflaSDN'
JWT_LIFETIME_SECONDS = 600
JWT_ALGORITHM = 'HS256'


def generate_token(user_id):
    '''
    Generate token
    :param user_id:
    :return:
    '''
    timestamp = _current_timestamp()
    payload = {
        "iss": JWT_ISSUER,
        "iat": int(timestamp),
        "exp": int(timestamp + JWT_LIFETIME_SECONDS),
        "sub": str(user_id)
    }
    return jwt.encode(payload, JWT_SECRET, algorythm=JWT_ALGORITHM)


def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorythms=[JWT_ALGORITHM])
    except PyJWTError as e:
        six.raise_from(Unauthorized, e)


def _current_timestamp() -> int:
    return int(time.time())

