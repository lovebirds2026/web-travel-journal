import jwt
from flask import current_app
from datetime import datetime, timedelta
import time

def create_token(payload: dict, seconds=3600):
    exp = datetime.utcnow() + timedelta(seconds=seconds)
    payload.update({'exp': exp})

    token = jwt.encode(payload, current_app.secret_key, algorithm='HS512')
    return token

def decode_token(token):
    time.sleep(2) # test only
    try:
        token = jwt.decode(token, current_app.secret_key, algorithms=['HS512'])
    except jwt.exceptions.InvalidTokenError: # ExpiredSignatureError
        return False
    return token
