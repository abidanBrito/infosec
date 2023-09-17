python3 Scanner.py configs/highScanner.json &
python3 Scanner.py configs/lowScanner.json &
sleep 0.5
# a valid transaction between a low-security card and the low-security scanner,
# that gets recorded by our sniffing device
python3 Card.py configs/lowCard.json 6666
echo "----------------------------------"

echo "Starting attack script"

sleep 0.5
python3 enc_without_auth.py c

trap "exit" INT TERM
trap "kill 0" EXIT
