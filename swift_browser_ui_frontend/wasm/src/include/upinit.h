/*
Upload process initialization functions.
*/

#include "uptypes.h"

#ifndef SWIFT_UI_UPLOAD_UPINIT_INCLUDED
#define SWIFT_UI_UPLOAD_UPINIT_INCLUDED

/*
Add a public key from ftw entry
*/
int add_recv_key(
    const char *path,
    const struct stat *st,
    int flag,
    struct FTW *ftws);

/*
Read in the receiver keys
*/
int read_in_recv_keys(struct ENCRYPT_SESSION *sess);

/*
Read in the keys for upload encryption
*/
int read_in_keys(
    char *passphrase,
    const struct UPLOAD_SESSION *resumableSession,
    struct ENCRYPT_SESSION *sess);

/*
Open and allocate an encrypted upload session
*/
struct SESSION *open_session_enc(
    const char *uploadId,
    const char *destContainer);

/*
Open and allocate an unencrypted upload session
*/
struct SESSION *open_session_unenc(
    const char *uploadId,
    const char *destContainer);

/*
Close and free an upload session
*/
void close_session(
    struct SESSION *sess);

#endif
