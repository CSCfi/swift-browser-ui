/*
Download service worker handlers.
*/

#include <stdint.h>
#include <errno.h>
#include <string.h>

#ifdef TEST
#include "stub_crypt4gh_header.h"
#include "stub_crypt4gh_segment.h"
#include "stub_crypt4gh.h"
#include "stub_sodium.h"
#include "stub_unistd.h"
#include "stub_fcntl.h"
#include <stdlib.h>
#else
#include <crypt4gh/header.h>
#include <crypt4gh/segment.h>
#include <crypt4gh.h>
#include <fcntl.h>
#include <unistd.h>
#include <sodium.h>
#endif //TEST


#include "include/uptypes.h"
#include "include/upinit.h"
#include "include/upcommon.h"

#include "include/streamingdownload.h"

uint8_t chunk_buf[65536];

/*
Open crypt4gh header for file decryption.
*/
uint8_t *get_session_key_from_header(const KEYPAIR *kp, const char *header)
{
    uint8_t *sessionkey;

    int ret = 0;
    int fd = open(header, O_RDONLY);

    uint8_t *keys = NULL;
    unsigned int nkeys = 0;
    uint64_t *edit_list = NULL;
    unsigned int edit_list_len = 0;

    ret = crypt4gh_header_parse(
        fd,
        kp->private,
        kp->public,
        &keys,
        &nkeys,
        &edit_list,
        &edit_list_len);

    if (edit_list != NULL && edit_list_len > 0)
    {
        sodium_free(edit_list);
    }

    if (keys != NULL && nkeys > 0)
    {
        return keys;
    }
    else
    {
        return NULL;
    }
}

/*
Decrypt a 64KiB + 22 chunk of data.
*/
CHUNK *decrypt_chunk(
    const uint8_t *session_key,
    uint8_t *segment,
    size_t len_segment)
{
    CHUNK *ret = allocate_chunk();
    memset(chunk_buf, 0, 65536);
    ret->chunk = chunk_buf;
    int retc = crypt4gh_segment_decrypt(
        session_key,
        segment,
        len_segment,
        ret->chunk,
        &(ret->len));

    return ret;
}
