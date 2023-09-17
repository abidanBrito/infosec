#!/usr/bin/env python3

import os
import os.path
import sys
import argparse
import getpass
import binascii
import json
from typing import Dict

from util import check_challenge

from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Hash import SHA256

# set by the company administrator
# we only want super long, military-grade passwords
PASSWORD_POLICY = 2


def read_password() -> str:
    password = getpass.getpass("Enter your master password:")

    if PASSWORD_POLICY == 0:
        if len(password) < 10:
            sys.stderr.write("Password not secure enough!\n")
            exit(-1)
    if PASSWORD_POLICY == 1:
        if len(password) < 20:
            sys.stderr.write("Password not secure enough!\n")
            exit(-1)
    if PASSWORD_POLICY == 2:
        if len(password) < 80:
            sys.stderr.write("Password not secure enough!\n")
            exit(-1)
    return password


def derive_encryption_key(password: str, salt: bytes) -> bytes:
    # output = 1 AES-256 key = 32 byte
    keylen = 32
    # iteration count for PBKDF2, 1 million is a good recommendation
    iterations = 1000000
    aes_key = PBKDF2(password, salt, dkLen=keylen,
                     count=iterations, hmac_hash_module=SHA256)
    return aes_key

def encrypt(plaintext: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, mode=AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    nonce = cipher.nonce
    result = nonce + tag + ciphertext
    return result 

def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    try:
        nonce = ciphertext[0:16]
        tag = ciphertext[16:32]
        ciphertext = ciphertext[32:]
        cipher = AES.new(key, mode=AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        sys.stderr.write("Invalid decryption\n")
        exit(-1)
    return plaintext


def verify_password(password: str, hex_digest: str) -> bool:
    hasher = SHA256.new()
    hasher.update(password.encode("utf-8"))
    hash = hasher.hexdigest()
    return hash == hex_digest


def query_vault(vault: Dict, key: bytes, query: str): 
    if query in vault:
        username_enc = binascii.unhexlify(vault[query]['user'])
        pass_enc = binascii.unhexlify(vault[query]['pass'])
        username = decrypt(username_enc, key)
        passw = decrypt(pass_enc, key)
        print("User:", username.decode("utf-8"))
        print("Pass:", passw.decode("utf-8"))
        return    

    sys.stderr.write("Could not find entry with id " + query + "\n")

def add_entry(vault: Dict, key: bytes, id: str, user: str, password: str): 
    if id in vault:
        print("Overriding entry " + id)
    

    username_enc = encrypt(user.encode("utf-8"), key)
    pass_enc = encrypt(password.encode("utf-8"), key)
    vault[id] = {'user': binascii.hexlify(username_enc).decode("utf-8"), 'pass': binascii.hexlify(pass_enc).decode("utf-8")}


def solve_challenge(vault_file):
    with open(vault_file, 'r') as f:
        vault = json.load(f)

    identifier = "InfoSec"
    password = ""
########################################################################
# enter your code here

########################################################################
    with open('password', 'w') as f:
        f.write(password)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', title='command')
    subparsers.required = True
    parser_n = subparsers.add_parser(
        'n', help='create new password vault at specified path')
    parser_n.add_argument('file')
    parser_q = subparsers.add_parser(
        'q', help='query password in specified password vault (will prompt for more information)')
    parser_q.add_argument('file')
    parser_a = subparsers.add_parser(
        'a', help='add (or override) password in specified password vault (will prompt for more information)')
    parser_a.add_argument('file')
    parser_c = subparsers.add_parser('c', help='challenge')
    parser_c.add_argument(
        'password_vault',
        nargs='?',
        default='vault.enc',
        help='default: vault.enc')
    args = parser.parse_args()

    if args.command == 'n':
        if os.path.isfile(args.file):
            print('vault already exists, please rename')
            return -1
        password = read_password()
        salt = os.urandom(16) 
        hasher = SHA256.new()
        hasher.update(password.encode("utf-8"))
        hash = hasher.hexdigest()
                
        vault = {
            "salt" : binascii.hexlify(salt).decode("utf-8"),
            "pw_hash" : hash,
            "vault" : {}
        }
        with open(args.file, 'w') as f:
            json.dump(vault, f)
        return

    if args.command == 'q':
        if not os.path.isfile(args.file):
            print('vault not found, please create vault first')
            return -1
        else:
            with open(args.file, 'r') as f:
                vault = json.load(f)
            salt = binascii.unhexlify(vault['salt'])
            password = read_password()
            if verify_password(password, vault['pw_hash']) == False:
                sys.stderr.write("invalid password\n")
                return -1
            key = derive_encryption_key(password, salt)
            query = input("identifier: ")
            query_vault(vault['vault'], key, query)
            return

    if args.command == 'a':
        if not os.path.isfile(args.file):
            print('vault not found, please create vault first')
            return -1
        else:
            with open(args.file, 'r') as f:
                vault = json.load(f)
            salt = binascii.unhexlify(vault['salt'])
            password = read_password()
            if verify_password(password, vault['pw_hash']) == False:
                sys.stderr.write("invalid password\n")
                return -1
            key = derive_encryption_key(password, salt)
            id = input("identifier: ")
            user = input("username: ")
            new_password = getpass.getpass("password: ")
            add_entry(vault['vault'], key, id, user, new_password)
            with open(args.file, 'w') as f:
                json.dump(vault, f)
            return


    if args.command == 'c':
        solve_challenge(args.password_vault)

        check_challenge('password')

        return


if __name__ == "__main__":
    sys.exit(main())
