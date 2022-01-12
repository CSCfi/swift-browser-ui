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
struct ENCRYPT_SESSION *current = NULL;

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
        fd = open(path, O_RDONLY);
        amount = read(fd, fout, 1023);
        // Skip if couldn't read from the file or current session is NULL
        if (amount <= 0 || !current)
        {
            printf("Failed to open the receiver key.\n");
            goto finalAddRecv;
        }
        // We need space for the new key inside encrypt session
        if (!current->recv_key_amount || !current->recv_keys)
        {
            current->recv_keys = malloc(
                sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES);
        }
        else
        {
            current->recv_keys = realloc(
                current->recv_keys,
                sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES * (current->recv_key_amount + 1));
        }
        amount = crypt4gh_public_key_from_blob(
            fout,
            amount,
            current->recv_keys + (sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES * current->recv_key_amount));
        if (amount)
        {
            current->recv_keys = realloc(
                current->recv_keys,
                sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES * (current->recv_key_amount));
        }
        else
        {
            printf("Pubkey read successful for %s\n", path);
            current->recv_key_amount++;
        }
    }
finalAddRecv:
    free(fout);
    close(fd);
    return 0;
}

/*
Read in the receiver keys
*/
int read_in_recv_keys(struct ENCRYPT_SESSION *sess) {
    int ret = -2;
    if (!sess) {
        goto finalReadRecv;
    }

    // Create an ephemeral keypair
    randombytes_stir();
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
    printf("Successfully read in the keys.\n");
    current = NULL;
    return ret;
}

/*
Read in the keys for upload encryption
*/
int read_in_keys(
    char *passphrase,
    struct ENCRYPT_SESSION *sess)
{
    // Read in the private key
    // We assume current working directory to be of the correct structure
    // JS side takes care of that
    int ret = 0;
    strncpy(sess->passphrase, passphrase, 1023);
    printf("%s\n", sess->passphrase);
    printf("Reading in the private key.\n");
    crypt4gh_private_key_from_file(
        "keys/pk.key",
        sess->passphrase ? sess->passphrase : "\0",
        sess->seckey,
        sess->pubkey);
    // Read in the receiving keys
    printf("Reading in the receiver keys.\n");
    current = sess;
    ret = nftw(
        "keys/recv_keys",
        &add_recv_key,
        5, // using at most 5 file descriptors for now
        FTW_PHYS);
finalReadIn:
    printf("Successfully read in the keys.\n");
    current = NULL;
    return ret;
}

/*
Open and allocate an encryption session
*/
struct ENCRYPT_SESSION *open_session_enc(void) {
    struct ENCRYPT_SESSION *ret = malloc(sizeof(struct ENCRYPT_SESSION));
    if (!ret) {
        return NULL;
    }
    // Initialize the encryption session
    ret->passphrase = calloc(1024, sizeof(char));
    ret->recv_keys = NULL;
    ret->recv_key_amount = 0;
    return ret;
}

/*
Close and free an upload session
*/
void close_session(
    struct ENCRYPT_SESSION *sess 
) {
    if (sess) {
        free(sess->recv_keys);
        free(sess->passphrase);
        free(sess);
    }
}
