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

// Global for current session to enable nice use of nftw
ENCRYPT_SESSION *current = NULL;

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
        printf("Adding receiver key in %s\n", path);
        fd = open(path, O_RDONLY);
        amount = read(fd, fout, 1023);
        // Skip if couldn't read from the file or current session is NULL
        if (amount <= 0)
        {
            printf("Failed to open the receiver key.\n");
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
    printf("Using %s for receiver folder path.\n", keypath);
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

/*
Read in the receiver keys
*/
int read_in_recv_keys(ENCRYPT_SESSION *sess) {
    int ret = -2;
    if (!sess) {
        goto finalReadRecv;
    }

    // Create an ephemeral keypair
    crypto_kx_keypair(
        sess->seckey,
        sess->pubkey
    );

    current = sess;
    ret = nftw(
        "keys/recv_keys",
        &add_recv_key,
        5, // use at most 5 file descriptors
        FTW_PHYS
    );
finalReadRecv:
    current = NULL;
    return ret;
}

/*
Read in the keys for upload encryption
*/
int read_in_keys(
    const char *passphrase,
    ENCRYPT_SESSION *sess)
{
    // Read in the private key
    // We assume current working directory to be of the correct structure
    // JS side takes care of that
    int ret = 0;
    strncpy(sess->passphrase, passphrase, 1023);
    crypt4gh_private_key_from_file(
        "keys/pk.key",
        sess->passphrase ? sess->passphrase : "\0",
        sess->seckey,
        sess->pubkey);
    // Read in the receiving keys
    current = sess;
    ret = nftw(
        "keys/recv_keys",
        &add_recv_key,
        5, // using at most 5 file descriptors for now
        FTW_PHYS);
finalReadIn:
    current = NULL;
    return ret;
}

/*
Open and allocate an encryption session
*/
ENCRYPT_SESSION *open_session_enc(void) {
    ENCRYPT_SESSION *ret = calloc(1, sizeof(ENCRYPT_SESSION));
    if (!ret) {
        return NULL;
    }
    // Initialize the encryption session
    ret->passphrase = (char*)malloc(1024 * sizeof(char));
    ret->recv_keys = NULL;
    ret->sessionkey = NULL;
    ret->recv_key_amount = 0;
    return ret;
}

/*
Close and free an upload session
*/
void close_session(
    ENCRYPT_SESSION *sess
) {
    if (sess != NULL) {
        if (sess->recv_keys != NULL) {
            free(sess->recv_keys);
        }
        if (sess->sessionkey != NULL) {
            sodium_free(sess->sessionkey);
        }
        if (sess->passphrase != NULL) {
            free(sess->passphrase);
        }
        free(sess);
    }
}
