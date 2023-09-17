#ifndef crypto_sign_h
#define crypto_sign_h

#include "api.h"
#define crypto_sign_PUBLICKEYBYTES CRYPTO_PUBLICKEYBYTES
#define crypto_sign_SECRETKEYBYTES CRYPTO_SECRETKEYBYTES
#define crypto_sign_BYTES CRYPTO_BYTES

int crypto_sign(
  unsigned char *sm,unsigned long long *smlen,
  const unsigned char *m,unsigned long long mlen,
  const unsigned char *sk
);

int crypto_sign_open(
  unsigned char *m,unsigned long long *mlen,
  const unsigned char *sm,unsigned long long smlen,
  const unsigned char *pk
);

int crypto_sign_keypair(unsigned char *pk,unsigned char *sk);

#endif
