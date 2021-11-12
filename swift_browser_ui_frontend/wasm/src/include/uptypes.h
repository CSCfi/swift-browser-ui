#include <stdint.h>
#include <sodium.h>
#include <uuid/uuid.h>

#ifndef SWIFT_UI_UPLOAD_TYPES
#define SWIFT_UI_UPLOAD_TYPES

// Encryption session storage
struct ENCRYPT_SESSION
{
    uint8_t seckey[crypto_kx_SECRETKEYBYTES];
    uint8_t pubkey[crypto_kx_PUBLICKEYBYTES];
    uint8_t *recv_keys;
    char *passphrase;
    unsigned int recv_key_amount;
};
#endif
