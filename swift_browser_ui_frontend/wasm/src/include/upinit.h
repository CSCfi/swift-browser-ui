/*
Upload process initialization functions.
*/

#include "uptypes.h"

#ifndef SWIFT_UI_UPLOAD_UPINIT_INCLUDED
#define SWIFT_UI_UPLOAD_UPINIT_INCLUDED

/*
Read in the keys for upload encryption
*/
int read_in_keys(
    const struct UPLOAD_SESSION *resumableSession,
    struct ENCRYPT_SESSION *sess);

/*
Open and allocate an upload session
*/
struct SESSION *open_session(
    const char *resumableId,
    const char *destContainer);

/*
Close and free an upload session
*/
void close_session(
    struct SESSION *sess);

#endif
