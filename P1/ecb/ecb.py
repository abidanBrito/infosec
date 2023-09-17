#!/usr/bin/env python3

import os
import os.path
import sys
import argparse

from util import check_challenge

from Cryptodome.Cipher import AES
from scipy.io import wavfile
from Cryptodome.Hash import SHA256
import numpy as np
import struct


def enc_audio(fname, key):
    cipher = AES.new(key=key, mode=AES.MODE_ECB)

    samplerate, pt = wavfile.read(fname)

    ct = []

    for sample in pt:
        ct_byte = cipher.encrypt(sample.tobytes() + bytes(15))
        ct.extend(struct.unpack("16B", ct_byte))

    wavfile.write(fname[:-4] + '_enc.wav', samplerate, np.array(list(ct)).astype(np.uint8))


def dec_audio(fname, key):
    cipher = AES.new(key=key, mode=AES.MODE_ECB)

    samplerate, ct = wavfile.read(fname)
    pt = []
    ct_bytes = bytearray(ct)

    for index in range(0, len(ct_bytes), 16):
        pt_bytes = cipher.decrypt(ct_bytes[index : index + 16])
        pt.append(pt_bytes[0])

    wavfile.write(fname[:-8] + "_dec.wav", samplerate, np.array(list(pt)).astype(np.uint8))


def solve_challenge(plain_audio_piece, enc_file):

    samplerate, enc = wavfile.read(enc_file)
    samplerate, plain_audio_piece = wavfile.read(plain_audio_piece)

    plain_audio = []
    
########################################################################
# enter your code here
    
    pt_bytes = bytearray(plain_audio_piece)
    ct_bytes = bytearray(enc)

    # NOTE(abi): we can find the offset programmatically. The PT audio piece is
    # part of the sniffed CT stream (zero-padded and encrypted).
    #
    # We can compare all PT blocks to the CT stream and shift the start when two
    # identical PT blocks yield different CT blocks. 

    dec_map = {}
    for ct in range(0, len(ct_bytes) - 16, 16):
        # All samples found (8-bit resolution)  
        if len(dec_map) == 256:
            break
        
        ct_block = ct
        for pt in range(0, len(pt_bytes)):
            ct_key = struct.unpack("16B", ct_bytes[ct_block : ct_block + 16])
            # Contradiction found, restart
            if ct_key in dec_map and dec_map[ct_key] != pt_bytes[pt]:
                dec_map.clear()
                break
            # Add new CT -> PT block map
            else:
                dec_map[ct_key] = pt_bytes[pt]
                ct_block += 16
    
    # Decrypt the sniffed stream swapping CT by PT blocks 
    for byte in range(0, len(ct_bytes), 16):
        plain_audio.append(dec_map[struct.unpack("16B", ct_bytes[byte : byte + 16])])
    
    # Cast to uint8 so it's playable
    plain_audio = np.uint8(plain_audio)

########################################################################
    
    wavfile.write("audio.wav", samplerate, np.array(plain_audio))

    hasher = SHA256.new()
    hasher.update(bytearray(plain_audio))

    with open("audio_hash", 'w') as f:
        f.write(hasher.hexdigest() + '\n')


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', title='command')
    subparsers.required = True
    parser_e = subparsers.add_parser('e', help='encrypt')
    parser_e.add_argument('file', nargs='+')
    parser_d = subparsers.add_parser('d', help='decrypt')
    parser_d.add_argument('file', nargs='+')
    parser_h = subparsers.add_parser('h', help='hash')
    parser_h.add_argument('file', nargs='+')
    parser_g = subparsers.add_parser('g', help='keygen')
    parser_c = subparsers.add_parser('c', help='challenge')
    parser_c.add_argument(
        'audio_piece',
        nargs='?',
        default='audio_piece.wav',
        help='default: audio_piece.wav')
    parser_c.add_argument(
        'sniffed_stream',
        nargs='?',
        default='sniffed_stream.wav',
        help='default: sniffed_stream.wav')
    args = parser.parse_args()

    if args.command == 'g':
        key = os.urandom(16)
        with open('key', 'wb') as f:
            f.write(key)
        return

    if args.command == 'e' or args.command == 'd':
        if not os.path.isfile('key'):
            print('no key found, run key generation first')
            return -1
        else:
            with open('key', 'rb') as f:
                key = f.read()
            files = [
                t for t in args.file if (
                    os.path.isfile(t) and not t == 'key')]

    if args.command == 'h':
        for f in args.file:
            if not os.path.splitext(f)[1] == '.wav':
                print('only .wav files allowed')
                return -1
            else:
                samplerate, audio = wavfile.read(f)
                hasher = SHA256.new()
                hasher.update(audio.tobytes())

                with open(f[:-4] + "_hash", 'w') as f:
                    f.write(hasher.hexdigest() + '\n')
                return

    if args.command == 'e':
        # we don't encrypt already encrypted files
        files = [t for t in files if not t.endswith('_enc.wav')]
        if len(files) == 0:
            print('No valid files selected')
            return

        for f in files:
            enc_audio(f, key)

        return

    if args.command == 'd':
        # we only want encrypted files
        files = [t for t in files if t.endswith('_enc.wav')]
        if len(files) == 0:
            print('No valid files selected')
            return

        for f in files:
            dec_audio(f, key)

        return

    if args.command == 'c':
        solve_challenge(args.audio_piece, args.sniffed_stream)

        check_challenge('audio_hash')

        return


if __name__ == "__main__":
    sys.exit(main())
