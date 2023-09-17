from Cryptodome.Random import get_random_bytes
import base64
import json

id_len = 8


def randID():
    rid = get_random_bytes(id_len)
    return base64.b64encode(rid).decode('utf-8')


lowCardID = randID()
highCardID = randID()
lowScannerID = randID()
highScannerID = randID()

highs = {
    "id": highScannerID,
    "allowedIDs": [highCardID],
    "high": True
}

lows = {
    "id": lowScannerID,
    "allowedIDs": [lowCardID],
    "high": False
}

highc = {
    "id": highCardID,
    "allowedIDs": [highScannerID],
    "high": True
}

lowc = {
    "id": lowCardID,
    "allowedIDs": [lowScannerID],
    "high": False
}

with open('configs/highScanner.json', 'w+') as f:
    json.dump(highs, f)

with open('configs/lowScanner.json', 'w+') as f:
    json.dump(lows, f)

with open('configs/highCard.json', 'w+') as f:
    json.dump(highc, f)

with open('configs/lowCard.json', 'w+') as f:
    json.dump(lowc, f)

with open('key.key', 'wb+') as f:
    f.write(get_random_bytes(16))
