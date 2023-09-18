/*
Init functions for folder upload
*/

#define _XOPEN_SOURCE 500
#include <unistd.h>
#include <fcntl.h>
#include <sodium.h>
#include <ftw.h>
#include <string.h>
#include <crypt4gh/key.h>
#include <uuid/uuid.h>
#include <stdio.h>

#include "include/uptypes.h"
#include "include/upinit.h"


/*
Read a public key from ftw entry
*/
uint8_t *recv_keys = NULL;
unsigned int recv_key_amount;


/*
Add a public key from ftw entry
*/
int add_recv_key(
    const char *path,
    const struct stat *st,
    int flag,
    struct FTW *ftws)
{
    // We'll use a 1024 byte buffer, enough for both ed25519 ssh and
    // c4gh keys.
    char *fout = calloc(1024, sizeof(char));
    unsigned char pub[crypto_kx_PUBLICKEYBYTES];
    int fd;
    int amount;

    if (flag == FTW_F)
    {
        #ifdef C4GH_WASM_DEv
        printf("Adding receiver key in %s\n", path);
        #endif
        fd = open(path, O_RDONLY);
        amount = read(fd, fout, 1023);
        // Skip if couldn't read from the file or current session is NULL
        if (amount <= 0)
        {
            #ifdef C4GH_WASM_DEv
            printf("Failed to open the receiver key.\n");
            #endif
            goto finalAddRecv;
        }
        // We need space for the new key inside encrypt session
        if (!recv_key_amount || !recv_keys)
        {
            recv_keys = malloc(
                sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES);
        }
        else
        {
            recv_keys = realloc(
                recv_keys,
                sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES * (recv_key_amount + 1));
        }
        amount = crypt4gh_public_key_from_blob(
            fout,
            amount,
            recv_keys + (sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES * recv_key_amount));
        if (amount)
        {
            recv_keys = realloc(
                recv_keys,
                sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES * (recv_key_amount));
        }
        else
        {
            recv_key_amount++;
        }
    }
finalAddRecv:
    free(fout);
    close(fd);
    return 0;
}

void libinit() {
    if (sodium_init() == -1) {
        #ifdef C4GH_WASM_DEV
        printf("Couldn't initialize sodium\n");
        #endif
        return;
    }

    // Main reason for init, only stir once to not run out of entropy
    randombytes_stir();
}


/*
Read in the receiver keys from a path
*/
CHUNK *read_in_recv_keys_path(const char *keypath) {
    #ifdef C4GH_WASM_DEV
    printf("Using %s for receiver folder path.\n", keypath);
    #endif
    int ret = nftw(
        keypath,
        &add_recv_key,
        5, // Use at most 5 file descriptors
        FTW_PHYS
    );

    if (ret) {
        return NULL;
    }

    CHUNK *retbuf = malloc(sizeof(CHUNK));

    retbuf->chunk = recv_keys;
    retbuf->len = recv_key_amount;
    recv_keys = NULL;
    recv_key_amount = 0;

    return retbuf;
}
