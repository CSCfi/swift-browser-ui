#include <stdint.h>
#include <sodium.h>
#include <uuid/uuid.h>

#ifndef SWIFT_UI_UPLOAD_TYPES
#define SWIFT_UI_UPLOAD_TYPES


/*
Struct for length aware chunk for easier interfacing with JS.
*/
typedef struct CHUNK
{
    uint8_t *chunk;
    size_t len;
} CHUNK;


/*
Struct for the encryption keypair.
*/
typedef struct KEYPAIR
{
    uint8_t private[crypto_kx_SECRETKEYBYTES];
    uint8_t public[crypto_kx_PUBLICKEYBYTES];
} KEYPAIR;


#endif
