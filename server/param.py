import os
from io import BytesIO
import numpy as np
import cv2
from datetime import datetime, timedelta, timezone
from Crypto.Util import Counter
from Crypto.Cipher import AES
import imghdr
import binascii
import base64

IMAGE_LIST = ["jpeg", "png"]
MAGIC = os.environ["MAGIC"]
KEY = binascii.unhexlify(os.environ["KEY"])


def is_in_time(epoc):
    curr = datetime.now(timezone.utc)
    delt = timedelta(hours=1)
    return (
        True
        if epoc < int((curr + delt).timestamp()) and epoc > int((curr - delt).timestamp())
        else False
    )


def is_valid_apikey(apikey):
    # NOTE: tsu-iscd/jcrypto support counter mode only.
    # apikey[0:31]: counter
    # apikey[32:96]: MAGIC
    # apikey[96:]: epoc
    if len(apikey) < 64 or len(apikey) & 1:
        return False
    ctr = Counter.new(128, initial_value=int(apikey[:32], 16))
    aes = AES.new(KEY, AES.MODE_CTR, counter=ctr)
    cipher = binascii.unhexlify(apikey[32:])
    plain = aes.decrypt(cipher)
    # TODO: 'binascii.Error: Non-hexadecimal digit found' should be handled.
    if binascii.unhexlify(plain[:32]).hex() != MAGIC:
        print(f"illegal magic: {binascii.unhexlify(plain[:32]).hex()}")
        return False
    if (len(plain[32:]) & 1) != 0:
        print(f"illegal plain: {plain[32:]}")
        return False
    epoc = int(binascii.unhexlify(plain[32:]).hex())
    if not is_in_time(epoc):
        print(f"illegal epoc: {epoc}")
        return False
    return True


def decode_image(encoded):
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except binascii.Error:
        print(f"decode error")
        return None
    image_type = imghdr.what(BytesIO(decoded))
    if image_type not in IMAGE_LIST:
        print(f"illegal image_type: {image_type}")
        return None

    image_np = np.fromstring(decoded, np.uint8)
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    if len(image.shape) != 3:
        print("illegal image format")
        return None
    '''
    height, width, _ = image.shape[:3]
    if height != 512 or width >= 1024:
        print(f"illegal image size: height={height}, width={width}")
        return None
    '''
    return image


def is_valid_param(body, result):
    version = body.get("version")
    device = body.get("device")
    apikey = body.get("apikey")
    image = body.get("image")
    tsumo = body.get("tsumo")
    print(f"version={version}, device={device}")
    if image is None or tsumo is None:
        return False
    if not is_valid_apikey(apikey):
        return False
    image = decode_image(image)
    if image is None:
        return False
    result["image"] = image
    result["tsumo"] = tsumo
    return True
