from flask import current_app
from werkzeug.utils import secure_filename

import jwt
from datetime import datetime, timedelta, UTC
import re
from pathlib import Path
from PIL import Image, ImageOps
from collections import namedtuple

import logging
log = logging.getLogger(__name__)

JWT_ALGO = 'HS512'
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'avif', 'png', 'webp', ] # pics only
QUALITY = 72
MAX_SIZE = 1920, 1280
THUMBNAIL_SIZE = 512, 512

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
    if not file or not allowed_photo_ext(file.filename):
        return

    filename = secure_filename(file.filename)
    # add timestamp
    filename = filename.rsplit('.', 1)[0] + '_' + timestamp_str + '.webp'
    dest_path = Path(current_app.config['UPLOAD_FOLDER_PHOTOS']) / filename
    thumb_path = Path(current_app.config['UPLOAD_FOLDER_THUMBS']) / filename

    try:
        with Image.open(file) as img: # Resize image and save in WebP format
            img = ImageOps.exif_transpose(img) # fix -90c rotation
            img.thumbnail(MAX_SIZE)
            img.save(dest_path, 'webp', quality=QUALITY)

            img.thumbnail(THUMBNAIL_SIZE)
            img.save(thumb_path, 'webp', quality=QUALITY)
    except Exception as e:
        log.error(f'Uploading image: {e}')

    size = dest_path.stat().st_size
    ImageInfo = namedtuple('ImageInfo', ('path', 'size'))
    return ImageInfo(filename, size)
