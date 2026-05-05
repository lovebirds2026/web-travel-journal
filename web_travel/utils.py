from flask import current_app
from werkzeug.utils import secure_filename

import jwt
from datetime import datetime, timedelta, UTC
import time
import re
from pathlib import Path
from collections import namedtuple

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

def save_photo(file) -> tuple | None:
    timestamp_str = str(datetime.now().timestamp()).split('.')[0]
    if file and allowed_photo_ext(file.filename):
        filename = secure_filename(file.filename)

        # add timestamp
        ext_index = filename.rfind('.')
        filename = filename[:ext_index] + '_' + timestamp_str + filename[ext_index:]
        dest = Path(current_app.config['UPLOAD_FOLDER_PHOTOS']) / filename
        file.save(dest)
        size = dest.stat().st_size
        ImageInfo = namedtuple('ImageInfo', ('path', 'size'))
        return ImageInfo(filename, size)
