import os
from datetime import datetime, timedelta, timezone
from Crypto.Util import Counter
from Crypto.Cipher import AES
import imghdr
import binascii

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
    if os.environment["development"]:
        return True
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


def is_valid_image(image):
    img_dec = base64.b64decode(image)
    if imghdr.what(BytesIO(img_dec)) not in IMAGE_LIST:
        return False
    img_np = np.formatstring(img_dec, np.uint8)
    image = cv2.imdecode(img_np)
    return True


def is_valid_param(event, context, result):
    version = data.get("version")
    device = data.get("device")
    apikey = data.get("apikey")
    image = data.get("image")
    tsumo = data.get("tsumo")
    print(f"version={version}, device={device}")
    if image is None or tsumo is None:
        return False
    if not is_valid_apikey(apikey):
        return False
    if not is_valid_imae(image):
        return False
    result["image"] = image
    result["tsumo"] = tsumo
    return True
