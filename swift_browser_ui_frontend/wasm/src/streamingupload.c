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

/*
Create a full header with the provided session key.
*/
CHUNK *create_header_from_key(
    const uint8_t *session_key_path,
    const uint8_t *session_key
) {
    // Get the list of parsed receivers
    KEYPAIR *kp = create_keypair();
    CHUNK *receivers = read_in_recv_keys_path(session_key_path);

    CHUNK *ret = create_crypt4gh_header(
        session_key,
        kp->private,
        receivers->chunk,
        receivers->len
    );

    free_keypair(kp);
    free_chunk(receivers);

    return ret;
}

/*
Encrypt a part of a file.
*/
CHUNK *encrypt_file_part(
    const uint8_t *session_key,
    size_t len_segment,
    const uint8_t *fpath,
    const size_t segment_offset
)
{
    CHUNK *ret = allocate_chunk();

    // Calculate the size of the encrypted segment.
    size_t cipherlen_segment = len_segment / 65536 * 65564
    if (len_segment % 65536 > 0) {
        cipherlen_segment += len_segment % 65536 + 28;
    }
    ret->chunk = malloc(cipherlen_segment);

    int fdinput = open(fpath, NULL, O_RDONLY);
    if (input == NULL) {
        return -1;
    }
    lseek(fdinput, segment_offset, SEEK_SET);

    uint8_t srcbuf[65536];
    int nread = 0;
    int nwrite = 0;

    for (let i = 0; i < cipherlen_segment; i + 65536) {
        nread = read(fdinput, srcbuf, 65536);
        crypt4gh_segment_encrypt(
            session_key,
            srcbuf,
            nread,
            ret->chunk + i,
            &nwrite
        );
        ret->len += nwrite;
    }

    return ret;
}
