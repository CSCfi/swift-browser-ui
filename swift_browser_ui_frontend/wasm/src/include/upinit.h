/*
Upload process initialization functions.
*/

#include <ftw.h>
#include "uptypes.h"

#ifndef SWIFT_UI_UPLOAD_UPINIT_INCLUDED
#define SWIFT_UI_UPLOAD_UPINIT_INCLUDED

/*********************
Sodium initialization.
*********************/
/*
Wrap libsodium initialization.
*/
void libinit();

/***************************
Receiver key initialization.
***************************/
/*
Add a public key from ftw entry
*/
int add_recv_key(
    const char *path,
    const struct stat *st,
    int flag,
    struct FTW *ftws);
/*
Read in the keys for upload encryption
*/
CHUNK *read_in_recv_keys_path(const char *keypath);

#endif
