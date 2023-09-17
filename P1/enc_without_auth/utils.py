from enum import Enum, auto

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Util.Padding import pad, unpad


class State(Enum):
    IDLE = auto(),
    WAIT = auto()


def encrypt(pt):
    with open('key.key', 'rb') as f:
        sharedkey = f.read()
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(sharedkey, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(pt, AES.block_size))

    return (iv, ct)


def decrypt(iv, ct):
    with open('key.key', 'rb') as f:
        sharedkey = f.read()
    try:
        cipher = AES.new(sharedkey, AES.MODE_CBC, iv)
        s = cipher.decrypt(ct)
        pt = unpad(s, AES.block_size)
    except ValueError:
        print('Value error occured during decryption')
        pt = None

    return pt
