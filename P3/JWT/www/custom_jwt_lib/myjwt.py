import hashlib
import hmac
import json
import os

from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

RS256 = 'RS256'
H256 = 'HS256'
supported_algorithms = [H256, RS256]

sign_key = None
verify_key = None

# -----------------------------------------------------------------------------
def load_private_key():
    private_key = open('keys/private-key.pem').read().strip()
    return private_key

# -----------------------------------------------------------------------------
def load_public_key():
    public_key = open('keys/public-key.pem').read().strip()
    return public_key

# -----------------------------------------------------------------------------
def load_random_bytes():
    return os.urandom()

# -----------------------------------------------------------------------------
def load_keys(alg):
    global sign_key
    global verify_key
    if alg == RS256:
        sign_key = load_private_key()
        verify_key = load_public_key()
    if alg == H256:
        sign_key = load_random_bytes()
        verify_key = sign_key

# -----------------------------------------------------------------------------
def encode_header_and_content_and_merge(jwt_header, jwt_content):
    json_header = b64encode(json.dumps(
        jwt_header).encode('utf-8')).decode('utf-8')
    json_payload = b64encode(json.dumps(
        jwt_content).encode('utf-8')).decode('utf-8')
    return f'{json_header}.{json_payload}'.encode('utf-8')

# -----------------------------------------------------------------------------
def sign_rsa(hdr_and_content_bytearray):
    if sign_key != None:
        private_rsakey = RSA.importKey(sign_key)
        signer = pkcs1_15.new(private_rsakey)
        digest = SHA256.new()
        digest.update(hdr_and_content_bytearray)
        signed_msg = signer.sign(digest)
        return signed_msg
    else:
        raise Exception('Sign key not found')

# -----------------------------------------------------------------------------
def encode(data_to_encode, algorithm):
    '''Encode a JWT token according to it's algorithm'''
    global sign_key
    global verify_key
    if sign_key == None or verify_key == None:
        raise Exception('Keys are None')

    if algorithm not in supported_algorithms:
        raise Exception('Algorithm not supported')

    jwt_header = {'alg': algorithm}

    hdr_and_content_bytearray = encode_header_and_content_and_merge(
        jwt_header, data_to_encode)

    if algorithm == H256:
        # sign content
        signature = hmac.new(str(sign_key).encode(
            'utf-8'), hdr_and_content_bytearray, hashlib.sha256).hexdigest()
        signature = b64encode(
            bytes(signature, encoding='utf-8')).decode('utf-8')
    elif algorithm == RS256:
        signed_msg = sign_rsa(hdr_and_content_bytearray)
        signature = b64encode(signed_msg).decode('utf-8')

    token = f"{hdr_and_content_bytearray.decode('utf-8')}.{signature}"
    return token

# -----------------------------------------------------------------------------
def split_token(token):
    split = token.split('.')
    hdr = json.loads(b64decode(split[0]))
    content = json.loads(b64decode(split[1]))
    signature = b64decode(split[2])
    algorithm = hdr['alg']
    return hdr, content, algorithm, signature

# -----------------------------------------------------------------------------
def decode(token):
    '''Decode a JWT token accordingly'''
    global sign_key
    global verify_key

    jwt_header, json_payload, algorithm, token_signature = split_token(token)
    if algorithm not in supported_algorithms:
        # no handling for algo='none' - since this can b exploited
        raise Exception('Algorithm not supported')
    hdr_and_content_bytearray = encode_header_and_content_and_merge(
        jwt_header, json_payload)

    if algorithm == H256:
        # sign content
        signature = hmac.new(str(verify_key).encode(
            'utf-8'), hdr_and_content_bytearray, hashlib.sha256).hexdigest()
        # note the signature is b64 decoded
        if (token_signature.decode('utf-8') == signature):
            return json_payload
        else:
            return None
    elif algorithm == RS256:
        # note the signature is b64 decoded
        # use public key to verify
        rsakey = RSA.importKey(verify_key.encode('utf-8'))
        digest = SHA256.new(hdr_and_content_bytearray)
        try:
            pkcs1_15.new(rsakey).verify(digest, token_signature)
            return json_payload
        except (ValueError, TypeError):
            return None
    return None
