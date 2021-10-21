#include <stdint.h>
#include <sodium.h>
#include <uuid/uuid.h>

#ifndef SWIFT_UI_UPLOAD_TYPES
#define SWIFT_UI_UPLOAD_TYPES

#ifndef SWIFT_UI_UPLOAD_CHUNK_SIZE
#define SWIFT_UI_UPLOAD_CHUNK_SIZE 5242880
#endif

// Encryption session storage
struct ENCRYPT_SESSION
{
    uint8_t seckey[crypto_kx_SECRETKEYBYTES];
    uint8_t pubkey[crypto_kx_PUBLICKEYBYTES];
    uint8_t *recv_keys;
    unsigned int recv_key_amount;
};

// Resumable file chunk upload data
struct UPLOADCHUNK
{
    unsigned int chunkNumber;      // Index number of the chunk
    unsigned int chunkSize;        // The size of the current chunk
    unsigned int totalSize;        // The total size of the upload
    char uploadFileIdentifier[37]; // The unique identifier for the upload
    unsigned int status;           // chunk status, 0 waiting, 1 uploading, 2 done, 3 error, 4 aborted
};

// Resumable file upload data
struct UPLOADFILE
{
    char *url;
    char *fileName;                // The upload file name
    char *relativePath;            // The upload full path
    char uploadFileIdentifier[37]; // The unique ID of the file upload
    unsigned int totalSize;        // The total size of the upload
    unsigned int totalChunks;      // The total chunk amount in the upload
    unsigned int isUploading;      // upload status, 0 waiting, 1 uploading, 2 done, 3 error, 4 aborted
    struct UPLOADCHUNK *chunks;
    struct UPLOADFILE *nextFile; // pointer to the next file
};

// Upload session storage
struct UPLOAD_SESSION
{
    char uploadIdStr[37];
    char *destContainer;
    char *destProject;
    struct UPLOADFILE *files;
    int total_files;
};

// Complete session storage containing both upload and encryption information
struct SESSION
{
    struct ENCRYPT_SESSION *encrypt;
    struct UPLOAD_SESSION *upload;
};

// Misc
#endif
