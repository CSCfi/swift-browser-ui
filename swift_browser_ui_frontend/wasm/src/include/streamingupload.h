/*
Encrypted file streaming functions.
*/


#include <stdint.h>

#include "uptypes.h"

#ifndef SWIFT_UI_UPLOAD_STREAMING_INCLUDED
#define SWIFT_UI_UPLOAD_STREAMING_INCLUDED


/*
Create an encryption key for session.
*/
uint8_t *create_session_key();


/*
Create the crypt4gh header using a set session key.
*/
CHUNK *create_crypt4gh_header(
    const uint8_t *session_key,
    const uint8_t *secret_key,
    const uint8_t *receivers,
    const unsigned int len_receivers
);


/*
Encrypt a 64KiB chunk of data.
*/
struct CHUNK *encrypt_chunk (
    const uint8_t *session_Key,
    uint8_t *segment,
    size_t len_segment
);

#endif
