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
Wrap crypt4gh header creation for access in JS side.
*/
struct CHUNK *wrap_crypt4gh_header(ENCRYPT_SESSION *sess);


/*
Encrypt a 64KiB chunk of data.
*/
struct CHUNK *encrypt_chunk (
    ENCRYPT_SESSION *sess,
    uint8_t *segment,
    size_t len_segment
);

#endif
