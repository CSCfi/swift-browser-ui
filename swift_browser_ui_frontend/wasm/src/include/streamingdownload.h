/*
Encrypted file download functions
*/

#include "uptypes.h"


#ifndef SWIFT_UI_DOWNLOAD_STREAMING_INCLUDED
#define SWIFT_UI_DOWNLOAD_STREAMING_INCLUDED


struct ENCRYPT_SESSION *open_decrypt_session();

char *get_session_public_key(struct ENCRYPT_SESSION *sess);

char *get_session_private_key(struct ENCRYPT_SESSION *sess);

char *get_session_key(struct ENCRYPT_SESSION *sess);

void open_crypt4gh_header(struct ENCRYPT_SESSION *sess);

struct CHUNK *decrypt_chunk(
    struct ENCRYPT_SESSION *sess,
    uint8_t* segment,
    size_t len_segment
);


#endif
