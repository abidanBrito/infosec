#!/usr/bin/env python3

import os
import os.path
import sys
import struct
import argparse

from util import check_challenge

from ecdsa import SigningKey, VerifyingKey, BadSignatureError, NIST256p, NIST192p
from ecdsa.util import sigdecode_string, randrange
from ecdsa.numbertheory import inverse_mod
from hashlib import sha256, sha1

curve = NIST256p
hashfunc = sha256

pkfile = 'ecc_key.pub'
skfile = 'ecc_key'

a = 743942
b = 830594370


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def sign_file(fname, sk, k):
    with open(fname, 'rb') as f:
        message = f.read()

    signature = sk.sign(message, k=k)

    with open(fname + '.sig', 'wb') as f:
        f.write(signature)


def verify_file(fname, vk):
    with open(fname, 'rb') as f:
        message = f.read()

    with open(fname + '.sig', 'rb') as f:
        sig = f.read()

    try:
        return vk.verify(sig, message)
    except (BadSignatureError):
        return False


def solve_challenge(file1, file2):
    with open(file1, 'rb') as f:
        f1 = f.read()

    with open(file1 + '.sig', 'rb') as f:
        sig1 = f.read()

    with open(file2, 'rb') as f:
        f2 = f.read()

    with open(file2 + '.sig', 'rb') as f:
        sig2 = f.read()

    (r1, s1) = sigdecode_string(sig1, curve.order)
    (r2, s2) = sigdecode_string(sig2, curve.order)

    z1 = int.from_bytes(hashfunc(f1).digest(), 'big')
    z2 = int.from_bytes(hashfunc(f2).digest(), 'big')

    n = curve.order

    d = 1
    ########################################################################
    # enter your code here

    #s1 s2 nach k umformen und beide k gleich setzten. Formel lösen
    divident_1 = -a*s2*z1 + (- b*s1*s2) + s1*z2
    divisor_1 = a*r1*s2 + (-r2*s1)
    d = inverse_mod(divisor_1,n)*divident_1 % n

    ########################################################################
    sk_rec = SigningKey.from_secret_exponent(d, curve, hashfunc)
    with open(skfile, 'wb') as f:
        f.write(sk_rec.to_pem())


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', title='command')
    subparsers.required = True
    parser_e = subparsers.add_parser('s', help='sign')
    parser_e.add_argument('file', nargs='+')
    parser_d = subparsers.add_parser('v', help='verify')
    parser_d.add_argument('file', nargs='+')
    parser_g = subparsers.add_parser('g', help='keygen')
    parser_c = subparsers.add_parser('c', help='challenge')
    parser_c.add_argument('file1', nargs='?', default='challenge_p1')
    parser_c.add_argument('file2', nargs='?', default='challenge_p2')
    args = parser.parse_args()

    if args.command == 'g':
        sk = SigningKey.generate(curve=curve, hashfunc=hashfunc)
        with open(skfile, 'wb') as f:
            f.write(sk.to_pem())

        vk = sk.get_verifying_key()
        with open(pkfile, 'wb') as f:
            f.write(vk.to_pem())

        return

    if args.command == 's' or args.command == 'v':
        files = [t for t in args.file if os.path.isfile(
            t) and not t.endswith('.sig')]

    if args.command == 's':
        if not os.path.isfile(skfile):
            print('no private key found, run key generation first!')
            return -1

        with open(skfile, 'rb') as f:
            sk = SigningKey.from_pem(f.read(), hashfunc)

        k = randrange(curve.order)
        for f in files:
            k = (a * k + b) % curve.order
            sign_file(f, sk, k)

        # ~ return

    if args.command == 'v':
        if not os.path.isfile(pkfile):
            print('no public key found, run key generation first!')
            return -1

        with open(pkfile, 'rb') as f:
            vk = VerifyingKey.from_pem(f.read())
        # there is a bug in the python library, the hashfunc does not get set when reading from pem
        vk.default_hashfunc = hashfunc

        for f in files:
            if not os.path.isfile(f + '.sig'):
                print(f + ': no signature found')
            else:
                verified = verify_file(f, vk)
                if verified:
                    print(f + ': OK')
                else:
                    eprint(f + ': verification failed!')

        return

    if args.command == 'c':
        if not os.path.isfile(pkfile):
            print('no public key found, restore original public key first!')
            return -1

        solve_challenge(args.file1, args.file2)
        check_challenge(skfile)


if __name__ == "__main__":
    sys.exit(main())
