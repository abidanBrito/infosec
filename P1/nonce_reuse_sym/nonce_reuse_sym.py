#!/usr/bin/env python3

import os
import os.path
import sys
import struct
import argparse
import json

from util import check_challenge

from Cryptodome.Cipher import AES

import lfsr
LFSR_LEN = 64
LFSR_TAPS = [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0,
             1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1]


def bitsToBytes(bit_array):
    assert len(bit_array) % 8 == 0, "only accept full bytes"
    for x in bit_array:
        assert x in (0, 1), "input not a bit array"
    res = []
    for i in range(0, len(bit_array), 8):
        byte = 0
        for j in range(8):
            byte |= bit_array[i+j] << (7-j)
        res.append(byte)

    return bytearray(res)


def bytesToBits(byte_array):
    res = []
    for x in byte_array:
        for j in range(8):
            bit = (x >> (7-j)) & 1
            res.append(bit)
    return res


def writeConfig(config):
    config["key"] = config["key"].hex()
    with open('key_config', 'w') as f:
        json.dump(config, f)


def readConfig():
    with open('key_config', 'rb') as f:
        config = json.load(f)
    config["key"] = bytes.fromhex(config["key"])
    return config

# implementation of the XKCD random number generator (https://xkcd.com/221/)


def getRandomNumber():
    return 4  # chosen by a fair dice roll, guaranteed to be random
    # RFC 1149.5 specifies 4 as the standard IEEE-vetted random number.


def getRandomNonce():
    r = getRandomNumber()
    return r.to_bytes(8, byteorder='little')


def openCar(config):
    nonce = getRandomNonce()
    cipher = AES.new(key=config["key"], mode=AES.MODE_CTR, nonce=nonce)

    l = lfsr.LFSR(LFSR_LEN, config["state"], LFSR_TAPS)
    car_code = l.output(LFSR_LEN)
    car_code = bitsToBytes(car_code)
    config["index"] += 1
    config["state"] = l.state

    ct = cipher.encrypt(car_code)
    fname = config["name"] + "." + str(config["index"]) + ".enc"

    # write the car unlock code
    with open(fname, 'wb') as f:
        print("write to ", fname)
        f.write(nonce)
        f.write(ct)

    # write back updated state to config file
    writeConfig(config)


def createNewChallenges(fname):
    # read current car state to get nonce
    with open(fname, 'rb') as f:
        nonce = f.read(8)
        state = f.read(8)

    state = bytesToBits(state)
    config = readConfig()
    l = lfsr.LFSR(LFSR_LEN, config["state"], LFSR_TAPS)
    l.output(LFSR_LEN)   # discard current car state

    # compute and encrypt 3 new car states
    for index_cntr in range(1, 4):
        new_state = bitsToBytes(l.output(LFSR_LEN))
        cipher = AES.new(key=config["key"], mode=AES.MODE_CTR, nonce=nonce)
        enc_state = cipher.encrypt(new_state)

        
        with open(f"challenge.{index_cntr}.enc", "wb") as f:
            f.write(nonce)
            f.write(enc_state)


def solve_challenge(challenge_fnames, solution_fname):
    challenge_files = challenge_fnames.split(",")
    nonces = []
    cts = []
    for filename in challenge_files:
        with open(filename, 'rb') as f:
            nonces.append(f.read(8))
            cts.append(f.read(8))

    next_nonce = bytes()
    next_ct = bytes()
########################################################################
# enter your code here

    next_nonce = getRandomNonce()
 
    # CT1 ^ CT2 = S1 ^ S2
    s12 = [a ^ b for a, b in zip(bytesToBits(cts[0]), bytesToBits(cts[1]))]

    # Initialize the register with S1 ^ S2
    l = lfsr.LFSR(LFSR_LEN, s12, LFSR_TAPS)

    # Discard initial state
    l.output(LFSR_LEN)

    # Clock n times to get new state (shifting) 
    # LFSR(S1 ^ S2) = S2 ^ S3
    s23 = l.output(LFSR_LEN)
    
    # LFSR(S2 ^ S3) ^ CT2 = CT2 ^ CT3 ^ CT2 = CT3
    next_ct = bitsToBytes([a ^ b for a, b in zip(s23, bytesToBits(cts[1]))])

########################################################################

    with open(solution_fname, 'wb') as f:
        f.write(next_nonce)
        f.write(next_ct)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', title='command')
    subparsers.required = True
    parser_d = subparsers.add_parser('o', help='create car unlocking code')
    parser_g = subparsers.add_parser('g', help='keygen')
    parser_e = subparsers.add_parser('e', help="create challenge files")
    parser_e.add_argument('config_file', nargs='?',
                          default='car.1.enc', help='default: car.1.enc')
    parser_c = subparsers.add_parser('c', help='challenge')
    parser_c.add_argument('challenge_files', nargs='?', default='challenge.1.enc,challenge.2.enc',
                          help='default: challenge.1.enc,challenge.2.enc')
    parser_c.add_argument('output_file', nargs='?',
                          default='challenge.3.enc', help='default: challenge.3.enc')
    args = parser.parse_args()

    if args.command == 'g':
        key = os.urandom(16)
        lfsr_state = bytesToBits(os.urandom(LFSR_LEN//8))
        config = {
            "name": "car",
            "key": key,
            "state": lfsr_state,
            "index": 0,
        }
        writeConfig(config)
        return

    if args.command == 'o':
        if not os.path.isfile('key_config'):
            print('no key_config found, run key generation first')
            return -1
        else:
            config = readConfig()

        openCar(config)

    if args.command == 'e':
        createNewChallenges(args.config_file)

    if args.command == 'c':
        solve_challenge(args.challenge_files, args.output_file)
        check_challenge(args.output_file)

        return


if __name__ == "__main__":
    sys.exit(main())
