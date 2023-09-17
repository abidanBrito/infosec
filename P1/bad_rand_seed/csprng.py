
from Cryptodome.Cipher import ChaCha20
from Cryptodome.Hash import SHA512

_prng = []
def csprng_seed(seed_bytes):
    digest = SHA512.new()
    digest.update(seed_bytes)
    d = digest.digest()
    
    key = d[:32]
    iv = d[32:40]
    chacha = ChaCha20.new(key=key, nonce=iv)
    
    global _prng
    _prng = chacha
    
def csprng_bytes(numbytes):
    return _prng.encrypt(b'\0' * numbytes)
