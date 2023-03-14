/*
Upload process initialization functions.
*/

#include <ftw.h>
#include "uptypes.h"

#ifndef SWIFT_UI_UPLOAD_UPINIT_INCLUDED
#define SWIFT_UI_UPLOAD_UPINIT_INCLUDED

/*
Wrapt libsodium initialization.
*/
void libinit();

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
int read_in_recv_keys(ENCRYPT_SESSION *sess);

/*
Read in the keys for upload encryption
*/
int read_in_keys(
    const char *passphrase,
    ENCRYPT_SESSION *sess);

/*
Open and allocate an encrypted upload session
*/
ENCRYPT_SESSION *open_session_enc(void);

/*
Close and free an upload session
*/
void close_session(
    ENCRYPT_SESSION *sess);

#endif
