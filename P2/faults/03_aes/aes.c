#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <faultconfig.h>
#include "tinyAES/aes.h"

uint8_t ct[16];

void decrypt(uint8_t *key, uint8_t *ct){
    // initialize the round keys
    struct AES_ctx ctx;
    AES_init_ctx(&ctx, key);
    
    AES_ECB_decrypt(&ctx, ct);
}

int main(int argc, char* argv[]) {
    // parse the input (the ciphertext)
    if(argc != 2 || strlen(argv[1]) != 32){
        printf("Usage: ./aes ct\n");
        printf("ct is a hex string (without 0x) of the 16 byte ciphertext to be decrypted\n");
        return 1;
    }
    
    char* in = argv[1];
    for (int i = 0; i < 32; i++) {
        sscanf(in, "%2hhx", &ct[i]);
        in += 2;
    }
    
    // read the key
    uint8_t key[16];
    FILE *fptr;
    char* fname = "key";
    if(access(fname , F_OK ) == -1)
        fname = "03_aes/key";
    fptr = fopen(fname, "rb");
    fread(key, 16, 1, fptr);
    fclose(fptr);
    
    decrypt(key, ct);
    
    for(int i = 0; i < 16; i++){
        printf("%02x", ct[i]);
    }
    printf("\n");
}

FAULT_CONFIG("TIMEOUT=30");
FAULT_CONFIG("NOZERO");
FAULT_CONFIG("NOHAVOC");
FAULT_CONFIG("NOSKIP");
FAULT_CONFIG("NOEXITMSG");
FAULT_CONFIG("MAXFAULTS=16");
FAULT_CONFIG_A("MAIN", decrypt);
