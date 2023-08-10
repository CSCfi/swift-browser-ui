/*
Encrypted file streaming functions.
*/


#include <stdint.h>

#include "uptypes.h"

#ifndef SWIFT_UI_UPLOAD_STREAMING_INCLUDED
#define SWIFT_UI_UPLOAD_STREAMING_INCLUDED


/*
Open an upload session.
*/
ENCRYPT_SESSION *open_session(const char *passphrase);


/*
Open an upload session with ephemeral keys.
*/
ENCRYPT_SESSION *open_session_eph();


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
Wrap crypt4gh header creation for access in JS side.
*/
struct CHUNK *wrap_crypt4gh_header(ENCRYPT_SESSION *sess);


/*
Encrypt a 64KiB chunk of data.
*/
struct CHUNK *encrypt_chunk (
    const uint8_t *session_Key,
    uint8_t *segment,
    size_t len_segment
);

#endif
