/*
Encrypted file download functions
*/

#include "uptypes.h"


#ifndef SWIFT_UI_DOWNLOAD_STREAMING_INCLUDED
#define SWIFT_UI_DOWNLOAD_STREAMING_INCLUDED


ENCRYPT_SESSION *open_decrypt_session();

char *get_session_public_key(ENCRYPT_SESSION *sess);

char *get_session_private_key(ENCRYPT_SESSION *sess);

char *get_session_key(ENCRYPT_SESSION *sess);

void open_crypt4gh_header(ENCRYPT_SESSION *sess);

struct CHUNK *decrypt_chunk(
    ENCRYPT_SESSION *sess,
    uint8_t* segment,
    size_t len_segment
);


#endif
