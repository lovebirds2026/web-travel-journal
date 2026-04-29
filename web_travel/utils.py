from flask import current_app
from werkzeug.utils import secure_filename

import jwt
from datetime import datetime, timedelta, UTC
import time
import re
from pathlib import Path

JWT_ALGO = 'HS512'
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'avif', 'png', ] # pics only

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

def allowed_photo_ext(filename) -> bool:
    if '.' in filename:
        parts = filename.split('.')
        if parts[0] and parts[-1].lower() in ALLOWED_EXTENSIONS:
            return True
    return False

def save_photo(file) -> bool:
    timestamp_str = str(datetime.now().timestamp()).split('.')[0]
    if file and allowed_photo_ext(file.filename):
        filename = secure_filename(file.filename)

        # add timestamp
        ind = filename.rfind('.')
        filename = filename[:ind] + '_' + timestamp_str + filename[ind:]
        file.save(Path(current_app.config['UPLOAD_FOLDER_PHOTOS']) / filename)
        return True
    return False
