/*
Common upload and download related functions
*/

#define _XOPEN_SOURCE 500
#include <stdint.h>
#include <errno.h>

#ifdef TEST
#include "stub_crypt4gh.h"
#include "stub_sodium.h"
#include <stdlib.h>
#include "stub_unistd.h"
#else
#include <crypt4gh.h>
#include <sodium.h>
#include <unistd.h>
#endif // TEST

#include "include/upcommon.h"
#include "include/upinit.h"
#include "include/uptypes.h"

/*
Generate download keypair
*/
KEYPAIR *create_keypair()
{
    KEYPAIR *ret = malloc(sizeof(KEYPAIR));

    crypto_kx_keypair(
        ret->public,
        ret->private);

    return ret;
}

/*
Free a keypair
*/
void free_keypair(KEYPAIR *kp)
{
    free(kp);
    return;
}

/*
Get crypt4gh public key
*/
uint8_t *get_keypair_public_key(KEYPAIR *kp)
{
    return kp->public;
}

/*
Get crypt4gh private key
*/
uint8_t *get_keypair_private_key(KEYPAIR *kp)
{
    return kp->private;
}

/*
Key init function, copied over from libcrypt4gh
*/
uint8_t *crypt4gh_session_key_new(void)
{
    if (sodium_init() == -1)
    {
        return NULL;
    }
    uint8_t *key = (uint8_t *)sodium_malloc(CRYPT4GH_SESSION_KEY_SIZE * sizeof(uint8_t));

    if (key == NULL || errno == ENOMEM)
    {
        return NULL;
    }

    /* Fill in with random data */
    randombytes_buf(key, CRYPT4GH_SESSION_KEY_SIZE);

    /* Mark it read-only */
    sodium_mprotect_readonly(key);
    return key;
}

/*
Free the crypt4gh session key with sodium.
*/
void free_crypt4gh_session_key(uint8_t *sk)
{
    sodium_free(sk);
}

/*
wrap filesystem item remove
*/
int nftwremove(
    const char *path,
    const struct stat *st,
    int flag,
    struct FTW *ftws)
{
    if (flag == FTW_F)
    {
        return unlink(path);
    }
    return 0;
}

/*
Wipe the temporary receiver keys used for building the receiver list.
*/
int rmrecv(const char *keypath)
{
    int ret;
    ret = nftw(
        keypath,
        &nftwremove,
        5, // use at most 5 file descriptors
        0);

    return ret;
}

/*
Allocate chunk.
*/
CHUNK *allocate_chunk()
{
    CHUNK *ret = malloc(sizeof(CHUNK));
    if (!ret)
    {
        return NULL;
    }
    ret->chunk = NULL;
    ret->len = 0;
    return ret;
}

/*
Wrap chunk length from pointer
*/
int wrap_chunk_len(CHUNK *chunk)
{
    return chunk->len;
}

/*
Wrap chunk content ptr get
*/
uint8_t *wrap_chunk_content(CHUNK *chunk)
{
    return chunk->chunk;
}

/*
Free chunk contents.
*/
void free_chunk(CHUNK *chunk)
{
    if (chunk->chunk)
    {
        free(chunk->chunk);
    }
    free(chunk);
    return;
}

/*
Free chunk with stack buffer
*/
void free_chunk_nobuf(CHUNK *chunk) {
    free(chunk);
    return;
}
