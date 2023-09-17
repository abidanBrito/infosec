#include <stdio.h>
#include <stdlib.h>
#include "ref10/crypto_sign.h"
#include "ref10/crypto_hash_sha512.h"

int main() {
    unsigned char pk[crypto_sign_PUBLICKEYBYTES];
    unsigned char sk[crypto_sign_SECRETKEYBYTES];
    crypto_sign_keypair(pk, sk);
    
    FILE *fptr;
    fptr = fopen("key", "wb");
    fwrite(sk, crypto_sign_SECRETKEYBYTES, 1, fptr);
    fclose(fptr);
    fptr = fopen("key.pub", "wb");
    fwrite(pk, crypto_sign_PUBLICKEYBYTES, 1, fptr);
    fclose(fptr);
    
    unsigned char az[64];
    crypto_hash_sha512(az, sk, 32);
    az[0] &= 248;
    az[31] &= 63;
    az[31] |= 64;
    
    fptr = fopen("a_solution", "wb");
    fwrite(az, 32, 1, fptr);
    fclose(fptr);
    
    return 0;
}
