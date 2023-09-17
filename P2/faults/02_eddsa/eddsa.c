#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <faultconfig.h>

#include "ref10/crypto_sign.h"

#define MAX_MESSAGE_LEN 2000

// after calling crypto sign, signed_message contains both the signature and the message
//   format: ( R (32 bytes) || s (32 bytes) || message (remaining bytes) )
unsigned char signed_message[crypto_sign_BYTES + MAX_MESSAGE_LEN];
unsigned long long signed_message_len;

int main(int argc, char* argv[]) {
    // parse the input (the ciphertext)
    if(argc != 2){
        printf("Usage: ./eddsa message\n");
        printf(" message is the thing you want to sign. If it contains spaces, then enclose the message in quotes.");
        return 1;
    }

    unsigned char pk[crypto_sign_PUBLICKEYBYTES];
    unsigned char sk[crypto_sign_SECRETKEYBYTES];    
    
    //read the keys
    FILE *fptr;
    char* fname = "key";
    if(access(fname , F_OK ) == -1)
        fname = "02_eddsa/key";
    fptr = fopen(fname, "rb");
    fread(sk, crypto_sign_SECRETKEYBYTES, 1, fptr);
    fclose(fptr);
    fname = "key.pub";
    if(access(fname , F_OK ) == -1)
        fname = "02_eddsa/key.pub";
    fptr = fopen(fname, "rb");
    fread(pk, crypto_sign_PUBLICKEYBYTES, 1, fptr);
    fclose(fptr);

    char* message = argv[1];
    int message_len = strlen(message);
    if(message_len > MAX_MESSAGE_LEN)
        message_len = MAX_MESSAGE_LEN;
    
    //sign the given message
    crypto_sign(signed_message, &signed_message_len, message, message_len, sk);
    
    //output the signed message ( Signature || Message )
    // where Signature = ( R (32 bytes) || s (32 bytes) )
    for(int i = 0; i < signed_message_len; i++){
        printf("%02x", signed_message[i]);
    }
    printf("\n");
    
    return 0;
}

FAULT_CONFIG("TIMEOUT=300");
FAULT_CONFIG("NOASLR");
FAULT_CONFIG("NOSKIP");
FAULT_CONFIG("NORIPTRIGGER");
FAULT_CONFIG("NOEXITMSG");
FAULT_CONFIG("MAXFAULTS=2");
FAULT_CONFIG_A("MAIN", main);
