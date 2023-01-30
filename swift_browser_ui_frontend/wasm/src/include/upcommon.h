/*
Upload process common functions
*/


#include <stdint.h>
#include "uptypes.h"


#ifndef SWIFT_UI_UPLOAD_COMMON
#define SWIFT_UI_UPLOAD_COMMON


/*
Key init function, from libcrypt4gh
*/
uint8_t* crypt4gh_session_key_new(void);

/*
Wipe the keys stored in FS.
*/
int rmrf();

/*
Allocate a chunk.
*/
CHUNK *allocate_chunk();

/*
Get chunk length from struct.
*/
int warp_chunk_len(CHUNK* chunk);


/*
Get chunk ptr from struct.
*/
uint8_t* wrap_chunk_content(CHUNK* chunk);

/*
Free a chunk from memory.
*/
void free_chunk (CHUNK* chunk);


/*
Release session resources.
*/
void clean_session(ENCRYPT_SESSION *sess);


#endif
