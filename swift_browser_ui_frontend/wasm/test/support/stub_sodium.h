#ifndef sodium_H
#define sodium_H

#define crypto_kx_SECRETKEYBYTES 32
#define crypto_kx_PUBLICKEYBYTES 32

int sodium_init(void);

int randombytes_stir(void);
void randombytes_buf(void *, unsigned long int);

void crypto_kx_keypair(unsigned char *, unsigned char *);

void *sodium_malloc(unsigned long int);
void sodium_free(void *);
void sodium_mprotect_readonly(void *);

#endif // sodium_H
