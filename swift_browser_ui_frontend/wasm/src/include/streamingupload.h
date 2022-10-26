/*
Encrypted file streaming functions.
*/


#include <stdint.h>

#include "uptypes.h"

#ifndef SWIFT_UI_UPLOAD_STREAMING_INCLUDED
#define SWIFT_UI_UPLOAD_STREAMING_INCLUDED


/*
Wipe the keys stored in FS.
*/
int rmrf();


/*
Open an upload session.
*/
struct ENCRYPT_SESSION *open_session(const char *passphrase);


/*
Open an upload session with ephemeral keys.
*/
struct ENCRYPT_SESSION *open_session_eph();


/*
Wrap crypt4gh header creation for access in JS side.
*/
struct CHUNK *wrap_crypt4gh_header(struct ENCRYPT_SESSION *sess);


/*
Allocate a chunk.
*/
struct CHUNK *allocate_chunk();


/*
Get chunk length from struct.
*/
int warp_chunk_len(struct CHUNK* chunk);


/*
Get chunk ptr from struct.
*/
uint8_t* wrap_chunk_content(struct CHUNK* chunk);


/*
Encrypt a 64KiB chunk of data.
*/
struct CHUNK *encrypt_chunk (
    struct ENCRYPT_SESSION *sess,
    uint8_t *segment,
    size_t len_segment
);


/*
Free a chunk from memory.
*/
void free_chunk (struct CHUNK* chunk);


/*
Release session resources.
*/
void clean_session(struct ENCRYPT_SESSION *sess);


#endif
