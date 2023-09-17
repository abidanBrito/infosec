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
high=None


class Scanner(object):
    state = None
    ID = None
    sentNonce = None
    allowedIDs = None
    currCard = None
    sniffed = None

    fulltranscript = None
    currtranscript = None

    def __init__(self, ID, allowedIDs, sniffed=False):
        self.ID = ID
        self.allowedIDs=allowedIDs
        self.fulltranscript = []
        self.currtranscript = []

        self.sniffed = sniffed

        self.resetState()

    def resetState(self):
        self.state = State.IDLE
        self.sentNonce = None
        self.currCard = None

        if len(self.currtranscript) > 0:
            self.fulltranscript += [self.currtranscript]

        self.currtranscript = []

        if self.sniffed and len(self.fulltranscript) > 0:
            with open("sniffed.json", "w+") as f:
                json.dump(self.fulltranscript, f)


    def receive(self, packet):
        self.currtranscript += [base64.b64encode(packet).decode('utf-8')]
        if self.state == State.IDLE:
            reply = self.process1(packet)
            if reply:
                self.currtranscript += [base64.b64encode(reply).decode('utf-8')]
            return (1, reply)
        elif self.state == State.WAIT:
            reply = self.process2(packet)
            return (2, reply)

    def process1(self, packet):
        print("Scanner: received a first message")

        if len(packet) != 3*aes_block_length:
            print("Scanner: Length mismatch")
            self.resetState()
            return None

        iv = packet[:aes_block_length]
        ct = packet[aes_block_length:2 * aes_block_length]
        cardNonce = packet[2 * aes_block_length:]

        cardID = decrypt(iv, ct)
        if (cardID is None) or (cardID not in self.allowedIDs):
            # unknown or invalid ID
            print('Scanner: the card ID is invalid or unknown')
            self.resetState()
            return None
        elif high:
            with open("highcard", "w") as f:
                f.write("high card accepted")

        self.currCard = cardID

        pt = cardID + bytes(self.ID) + cardNonce

        (iv, ct) = encrypt(pt)
        self.sentNonce = get_random_bytes(16)
        packet = iv + ct + self.sentNonce
        self.state = State.WAIT

        print("Scanner: message OK, send reply")

        return packet

    def process2(self, packet):
        print("Scanner: received second message")

        if len(packet) != 5*aes_block_length:
            print("Scanner: Length mismatch")
            self.resetState()
            return False

        iv = packet[:aes_block_length]
        ct = packet[aes_block_length:]
        pt = decrypt(iv, ct)
        if pt is None:
            print('Scanner: empty packet')
            self.resetState()
            return False

        receivedCardID = pt[:id_len]
        c = id_len
        receivedScannerID = pt[c:c + id_len]
        c += id_len
        receivedSessionID = pt[c:c + aes_block_length]
        c += aes_block_length
        receivedNonce = pt[c:c + aes_block_length]
        c += aes_block_length
        command = pt[c:]

        if (receivedCardID != self.currCard) or (
                receivedScannerID != self.ID) or (
                        receivedNonce != self.sentNonce):
            print('Scanner: there is a problem with the ID or the nonce')
            self.resetState()
            return False

        self.resetState()
        if command == commanddoor:
            if high:
                print('Scanner: opened high security door')
                print('Challenge solved! (in case you didn\'t use a high-security card...)')
                with open("highdoor", "w") as f:
                    f.write("opened high door")
            else:
                print('Scanner: opened low security door')
            return True
        else:
            print('Scanner: command was not understood')
            return False


def main():
    global high
    with open(sys.argv[1], 'r') as f:
        config = json.load(f)
    
    selfID = base64.b64decode(config["id"])
    allowedIDs = [base64.b64decode(c) for c in config["allowedIDs"]]
    high = config["high"]

    if high:
        port = 6667
    else:
        port = 6666

    scanner = Scanner(selfID, allowedIDs, sniffed = not high)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind( (HOST, port) )
        s.listen()

        while True:
            conn, __ = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    # print(f"Scanner: received {data}")
                    (state, reply) = scanner.receive(data)
                    if state == 2:
                        break
                    if reply == None:
                        print("Scanner: Abort current connection")
                        break
                    conn.sendall(reply)

if __name__ == "__main__":
    sys.exit(main())
