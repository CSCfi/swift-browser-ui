/*
Upload process common functions
*/


#include <stdint.h>
#include "uptypes.h"


#ifndef SWIFT_UI_UPLOAD_COMMON
#define SWIFT_UI_UPLOAD_COMMON


/*****************************************************
Encryption / decryption keypair convenience functions.
*****************************************************/
/*
Allocate and wrap encryption / decryption keypair creation.
*/
KEYPAIR *create_keypair();
/*
Free a previously allocated keypair.
*/
void free_keypair(KEYPAIR *kp);
/*
Return public key from the keypair.
*/
uint8_t *get_keypair_public_key(KEYPAIR *kp);
/*
Return private key from the keypair.
*/
uint8_t *get_keypair_private_key(KEYPAIR *kp);


/*
Key init function, from libcrypt4gh
*/
uint8_t *crypt4gh_session_key_new(void);


/***************************************************
Encryption / decryption chunk convenience functions.
***************************************************/
/*
Allocate a chunk.
*/
CHUNK *allocate_chunk();
/*
Get chunk length from struct.
*/
int warp_chunk_len(CHUNK *chunk);
/*
Get chunk ptr from struct.
*/
uint8_t *wrap_chunk_content(CHUNK *chunk);
/*
Free a chunk from memory.
*/
void free_chunk (CHUNK *chunk);


#endif
