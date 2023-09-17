# Encryption without Authentication

This exercise has a different structure than all of the other exercises, so we aim to provide some additional information here to help you understand the overall system.

There are two different roles, scanners and cards. A card is a representation of a physical NFC card with an id and an embedded secret key. A scanner is a representation of the physical scanner on the door, that also has the same secret key and an id. Both the card and scanner also have lists of allowed ids, representing devices that they are allowed to communicate with. You can find this information in the `configs/*.json` files.

The scenario is the following: You are in possession of a powerful network sniffing device, that can read all packets sent between a scanner and a card.
However, the scanner is only installed on the outer, low-security door, so you can only observe protocol executions between the low-security scanner and low-security cards.
Your goal is to successfully open the high-security door, using information obtained by a protocol execution on this lower-level scanner.

You can interact with the Scanner interfaces using the functionality in `enc_without_auth.py`. The provided script `enc_without_auth.sh` shows how the overall system is set up and how your attack will be executed. In the beginning, a transaction between a low-security card and scanner will be executed, and your sniffing device will record the network packets that are sent into `sniffed.json`. Your attack will be executed when calling `enc_without_auth.py c`, where you can use this sniffed information and also connect and send packets to the scanners. Finally, your goal is to successfully open the high-security door by interacting with the high-security scanner, without actually being in possession of a high-security card.

Some notes on tests: On the test system, you will not have access to the secret key, you can only use the provided network interfaces to communicate with the scanners, as well as the transcript of the opening of the low-security door in `sniffed.json`. For testing, you however can generate a new key file and the ids of the cards and scanners using the provided `create_config.py`.