#include <stdint.h>
#include <sodium.h>
#include <uuid/uuid.h>

#ifndef SWIFT_UI_UPLOAD_TYPES
#define SWIFT_UI_UPLOAD_TYPES

// Encryption session storage
typedef struct ENCRYPT_SESSION
{
    unsigned char seckey[crypto_kx_SECRETKEYBYTES];
    unsigned char pubkey[crypto_kx_PUBLICKEYBYTES];
    unsigned char *recv_keys;
    unsigned int recv_key_amount;
};

// Upload session storage
typedef struct UPLOAD_SESSION
{
    char *resumableIdStr[37];
    char *destContainer;
};

// Complete session storage containing both upload and encryption information
typedef struct SESSION
{
    struct ENCRYPT_SESSION *encrypt;
    struct UPLOAD_SESSION *upload;
};

// Resumable file upload data
typedef struct RESUMABLEFILE
{
    const char *url;
    const uint64_t resumableTotalSize;
    const uint64_t resumableTotalChunks;
    unsigned int isUploading;
};

// Resumable file chunk upload data
typedef struct RESUMABLECHUNK
{
    const uint64_t resumableChunkNumber;
    const uint64_t resumableChunkSize;
    const uint64_t resumableTotalSize;
    const char *resumableIdentifier;
};
#endif
