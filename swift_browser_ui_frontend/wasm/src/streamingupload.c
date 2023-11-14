/*
Upload service worker handlers
*/

#define _XOPEN_SOURCE 500

#include <stdint.h>
#include <errno.h>
#include <unistd.h>

#ifdef TEST
#include "stub_crypt4gh_header.h"
#include "stub_crypt4gh_segment.h"
#include "stub_crypt4gh.h"
#include <stdlib.h>
#else
#include <crypt4gh/header.h>
#include <crypt4gh/segment.h>
#include <crypt4gh.h>
#endif // TEST

#include "include/uptypes.h"
#include "include/upinit.h"
#include "include/upcommon.h"

#include "include/streamingupload.h"

/*
Create a session key for single upload.
*/
uint8_t *create_session_key()
{
    uint8_t *ret = crypt4gh_session_key_new();
    return ret;
}

/*
Create crypt4gh header
*/
CHUNK *create_crypt4gh_header(
    const uint8_t *session_key,
    const uint8_t *secret_key,
    const uint8_t *receivers,
    const unsigned int len_receivers)
{
    CHUNK *ret = allocate_chunk();

    int err = crypt4gh_header_build(
        session_key,
        secret_key,
        receivers,
        len_receivers,
        &(ret->chunk),
        &(ret->len));

    return ret;
}

/*
Encrypt a 64KiB chunk of data.
*/
CHUNK *encrypt_chunk(
    const uint8_t *session_key,
    uint8_t *segment,
    size_t len_segment)
{
    CHUNK *ret = allocate_chunk();
    ret->chunk = malloc(CRYPT4GH_CIPHERSEGMENT_SIZE * sizeof(uint8_t));
    crypt4gh_segment_encrypt(
        session_key,
        segment,
        len_segment,
        ret->chunk,
        &(ret->len));
    return ret;
}
