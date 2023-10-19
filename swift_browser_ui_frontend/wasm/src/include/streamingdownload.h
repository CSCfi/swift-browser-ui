/*
Encrypted file download functions
*/

#include "uptypes.h"


#ifndef SWIFT_UI_DOWNLOAD_STREAMING_INCLUDED
#define SWIFT_UI_DOWNLOAD_STREAMING_INCLUDED


/*
Open crypt4gh header for file decryption and return session key.
*/
uint8_t *get_session_key_from_header(const KEYPAIR *kp, const char *header);


/*
Decrypt a crypt4gh encrypted chunk using the session key.
*/
CHUNK *decrypt_chunk(
    const uint8_t *session_key,
    uint8_t *segment,
    size_t len_segment
);


#endif
