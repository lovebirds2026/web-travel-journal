import jwt
from flask import current_app
from datetime import datetime, timedelta, UTC
import time
import re

JWT_ALGO = 'HS512'

def create_token(payload: dict, seconds=3600):
    exp = datetime.now(UTC) + timedelta(seconds=seconds)
    payload.update({'exp': exp})

    token = jwt.encode(payload, current_app.secret_key, algorithm=JWT_ALGO)
    return token

def decode_token(token):
    try:
        token = jwt.decode(token, current_app.secret_key, algorithms=[JWT_ALGO])
    except jwt.exceptions.InvalidTokenError: # expired/invalid signature
        return False
    return token

def check_email_input(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))