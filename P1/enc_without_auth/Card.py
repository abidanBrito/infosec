#!/usr/bin/python3
from utils import State
from utils import encrypt, decrypt
from Cryptodome.Random import get_random_bytes
import sys
import socket
import json
import base64

id_len = 8
aes_block_length = 16
commanddoor = "opendoor".encode("utf-8")
HOST='0.0.0.0'
PORT=6666

class Card(object):
    ID = None
    state = None

    allowedIDs = None
    sentNonce = None
    sessionID = None

    def __init__(self, ID, allowedIDs):
        self.ID = ID
        self.allowedIDs=allowedIDs
        self.resetState()

    def resetState(self):
        self.state = State.IDLE
        self.sentNonce = None
        self.sessionID = None

    """
    The first packet contains the encrypted ID and a random challenge nc
    """
    def packet1(self):
        
        # generate random challenge
        nonce = get_random_bytes(aes_block_length)
        # encrypt your ID
        (iv, ct) = encrypt(self.ID)
        # build the packet
        packet = iv + ct + nonce
        #print("Card: Sent enc("+str(self.ID)+")="+str(iv)+str(ct)+" and nonce " + str(nonce))
        self.sentNonce = nonce
        self.state = State.WAIT
        return packet
        

    """
    The second packet contains the encrypted scanner and card ID, 
    a new, random session ID, 
    and the scanner nonce alongside with the command
    """
    def packet2(self, packet):
        print("Card: received reply from Scanner")

        # encrypted challenge & scanner ID, challenge nonce
        iv = packet[:aes_block_length]
        ct = packet[aes_block_length:4 * aes_block_length]
        scannerNonce = packet[4 * aes_block_length:]

        pt = decrypt(iv, ct)
        if pt is None:
            print('Card: received nothing')
            self.resetState()
            return None

        receivedCardID = pt[:id_len]
        receivedScannerID = pt[id_len:2 * id_len]
        receivedChallenge = pt[2 * id_len:]
        if self.ID != receivedCardID: 
            print('Card: This is not for me, my ID is different')
            self.resetState()
            return None
        if receivedScannerID not in self.allowedIDs: 
            print('Card: This is not an allowed ID')
            self.resetState()
            return None
        if receivedChallenge != self.sentNonce:
            print('Card: This is not the nonce I sent')
            self.resetState()
            return None

        # scanner nonce
        self.sessionID = get_random_bytes(aes_block_length)
        command = commanddoor
        pt = self.ID + receivedScannerID + self.sessionID + \
            scannerNonce + command
        (iv, ct) = encrypt(pt)
        packet = iv + ct

        self.resetState()  # reset state

        print("Card: message OK, send reply to scanner")

        return packet
    
    def opendoor(self):
        print("Card: initiate open")

        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        
        p1 = self.packet1()
        if p1 is None:
            print("Card: abort")
            sys.exit(1)
        s.sendall(p1)
        data=s.recv(1024)
        if not data:
            print("Card: no reply received, abort")
            sys.exit(1)
        p2 = self.packet2(data)
        if p2 is None:
            print("Card: incorrect data received, abort")
            sys.exit(1)
        s.sendall(p2)
        
        s.close()

def main():
    global PORT
    
    with open(sys.argv[1], 'r') as f:
        config = json.load(f)
    
    PORT = int(sys.argv[2])
    
    selfID = base64.b64decode(config["id"])
    allowedIDs = [base64.b64decode(c) for c in config["allowedIDs"]]
    high = config["high"]
    
    c = Card(selfID, allowedIDs)
    c.opendoor()

    return 0
        
    

if __name__ == "__main__":
    sys.exit(main())
