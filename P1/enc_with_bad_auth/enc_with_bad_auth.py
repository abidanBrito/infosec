#!/usr/bin/env python3

import os
import os.path
import sys
import argparse

from util import check_challenge

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad  # pkcs7 is standard


def cbc_mac(message, key):
    cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=b'\x00' * 16)
    return cipher.encrypt(message)[-AES.block_size:]


def cbc_encrypt(message, key):
    cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=b'\x00' * 16)
    return cipher.encrypt(message)


def cbc_decrypt(ciphertext, key):
    cipher = AES.new(key=key, mode=AES.MODE_CBC, iv=b'\x00' * 16)
    return cipher.decrypt(ciphertext)


def enc_text(fname, key):
    with open(fname, 'rb') as f:
        message = f.read()

    padded_message = pad(message, AES.block_size)
    ct = cbc_encrypt(padded_message, key)

    with open(fname + '.enc', 'wb') as f:
        f.write(ct)


def dec_text(fname, key):
    with open(fname, 'rb') as f:
        ct = f.read()

    # decrypt authenticated ciphertext
    pt = cbc_decrypt(ct, key)

    with open(fname[:-len(".enc")], 'wb') as f:
        f.write(unpad(pt, AES.block_size))


def mac_then_enc_text(fname, key):
    with open(fname, 'rb') as f:
        message = f.read()

    padded_message = pad(message, AES.block_size)
    ct = cbc_encrypt(padded_message + cbc_mac(padded_message, key), key)

    with open(fname + '.authenc', 'wb') as f:
        f.write(ct)


def dec_and_verify_text(fname, key):
    with open(fname, 'rb') as f:
        ct = f.read()

    # decrypt authenticated ciphertext
    pt = cbc_decrypt(ct, key)

    # split plaintext up into message and tag
    padded_message = pt[:-AES.block_size]
    tag = pt[-AES.block_size:]

    # recompute tag and compare to given tag
    tag_rec = cbc_mac(padded_message, key)
    if tag != tag_rec:
        print(fname + ': Decryption failed.')
        return -1

    with open(fname[:-len(".authenc")], 'wb') as f:
        f.write(unpad(padded_message, AES.block_size))


def solve_challenge(captured_enc_file, captured_authenc_file):
    # captured ciphertext of challenge, without authentication
    with open(captured_enc_file, 'rb') as f:
        captured_enc = f.read()
    # captured authenticated ciphertext of non-challenge plaintext
    with open(captured_authenc_file, 'rb') as f:
        captured_authenc = f.read()

    auth_enc = b''
    ########################################################################
    # enter your code here
    captured_authenc_tag = captured_authenc[48:64]
    auth_enc = captured_enc + captured_authenc_tag

    #public key, we can use the same tag for the new one
    tag = captured_authenc[-AES.block_size:]
    auth_enc = captured_enc + tag

    ########################################################################
    with open('challenge.authenc', 'wb') as f:
        f.write(auth_enc)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', title='command')
    subparsers.required = True
    parser_e = subparsers.add_parser('e', help='mac-then-encrypt')
    parser_e.add_argument('file', nargs='+')
    parser_d = subparsers.add_parser('d', help='decrypt-and-verify')
    parser_d.add_argument('file', nargs='+')
    parser_e_old = subparsers.add_parser('old_e', help='encrypt')
    parser_e_old.add_argument('file', nargs='+')
    parser_d_old = subparsers.add_parser('old_d', help='decrypt')
    parser_d_old.add_argument('file', nargs='+')
    parser_g = subparsers.add_parser('g', help='keygen')
    parser_c = subparsers.add_parser('c', help='challenge')
    parser_c.add_argument('captured_authenc_file',
                          nargs='?', default='marauder.authenc')
    parser_c.add_argument('captured_enc_file', nargs='?',
                          default='challenge.enc')
    args = parser.parse_args()

    if args.command == 'g':
        key = os.urandom(16)
        with open('key', 'wb') as f:
            f.write(key)
        return

    if args.command in ['e', 'd', 'old_e', 'old_d']:
        if not os.path.isfile('key'):
            print('no key found, run key generation first')
            return -1
        else:
            with open('key', 'rb') as f:
                key = f.read()
            files = [
                t for t in args.file if (
                    os.path.isfile(t) and not t == 'key')]

    if args.command == 'old_e':
        # we don't encrypt already encrypted files
        files = [t for t in files if not t.endswith('.enc')]
        if len(files) == 0:
            print('No valid files selected')
            return

        for f in files:
            enc_text(f, key)

        return

    if args.command == 'e':
        # we don't encrypt already encrypted files
        files = [t for t in files if not t.endswith('.authenc')]
        if len(files) == 0:
            print('No valid files selected')
            return

        for f in files:
            mac_then_enc_text(f, key)

        return

    if args.command == 'old_d':
        # we only want encrypted files
        files = [t for t in files if t.endswith('.enc')]
        if len(files) == 0:
            print('No valid files selected')
            return

        for f in files:
            dec_text(f, key)

        return

    if args.command == 'd':
        # we only want encrypted files
        # old version: files = [t for t in files if t.endswith('.enc')]
        files = [t for t in files if t.endswith('.authenc')]
        if len(files) == 0:
            print('No valid files selected')
            return

        for f in files:
            # old version: dec_text(f, key)
            dec_and_verify_text(f, key)

        return

    if args.command == 'c':
        if not args.captured_enc_file.endswith('.enc'):
            print('Not a valid enc file selection')
            return
        if not args.captured_authenc_file.endswith('.authenc'):
            print('Not a valid authenc file selection')
            return
        solve_challenge(args.captured_enc_file, args.captured_authenc_file)
        check_challenge(args.captured_enc_file[:-4])

        return


if __name__ == "__main__":
    sys.exit(main())
