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
    printf("add_recv_key called\n");
    char *fout = calloc(1024, sizeof(char));
    unsigned char pub[crypto_kx_PUBLICKEYBYTES];
    int fd;
    int amount;

    if (flag == FTW_F)
    {
        printf("Is a file. Reading in receiving key.");
        fd = open(path, O_RDONLY);
        amount = read(fd, fout, 1023);
        // Skip if couldn't read from the file or current session is NULL
        if (amount <= 0 || !current)
        {
            printf("Failed to open the receiver key.\n");
            goto finalAddRecv;
        }
        // Reuse amount for pubkey return value
        // amount = crypt4gh_public_key_from_blob(
        //     fout,
        //     amount,
        //     pub);
        // if (amount)
        // {
        //     printf("Failed to decode the receiver key\n");
        //     goto finalAddRecv;
        // }
        // We need space for the new key inside encrypt session
        if (!current->recv_key_amount || !current->recv_keys)
        {
            printf("Allocating the initial key slot\n");
            current->recv_keys = malloc(
                sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES);
        }
        else
        {
            printf("Allocating a new key slot\n");
            current->recv_keys = realloc(
                current->recv_keys,
                sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES * (current->recv_key_amount + 1));
        }
        printf("Reading in the receiver public key.\n");
        amount = crypt4gh_public_key_from_blob(
            fout,
            amount,
            current->recv_keys + (sizeof(unsigned char) * crypto_kx_PUBLICKEYBYTES * current->recv_key_amount));
        if (amount)
        {
            printf("Key read unsuccessful for %s, unallocate key memory.\n", path);
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
    char *passphrase,
    const struct UPLOAD_SESSION *uploadSession,
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
        // passphrase,
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
    // free(passphrase);
    // chdir("..");
    return ret;
}

/*
Open and allocate an encrypted upload session
*/
struct SESSION *open_session_enc(
    const char *uploadId,
    const char *destContainer)
{
    printf("Allocating the encrypted upload session.\n");
    struct SESSION *ret = malloc(sizeof(struct SESSION));
    // Allocate encrypt and upload sessions
    ret->upload = malloc(sizeof(struct UPLOAD_SESSION));
    ret->encrypt = malloc(sizeof(struct ENCRYPT_SESSION));
    // Initialize the sessions
    ret->upload->destContainer = malloc(strlen(destContainer + 1));
    strcpy(ret->upload->destContainer, destContainer);
    strcpy(ret->upload->uploadIdStr, uploadId);
    ret->encrypt->passphrase = calloc(1024, sizeof(char));
    ret->encrypt->recv_keys = NULL;
    ret->encrypt->recv_key_amount = 0;
    printf("Successfully allocated the encrypted upload session.\n");
    return ret;
}

/*
Close and free an upload session
*/
void close_session(
    struct SESSION *sess)
{
    printf("Closing the upload session.\n");
    if (sess->encrypt)
    {
        if (sess->encrypt->recv_keys)
        {
            printf("Freeing the receiver keys\n");
            free(sess->encrypt->recv_keys);
        }
        if (sess->encrypt->passphrase) {
            printf("Freeing the key passphrase\n");
            free(sess->encrypt->passphrase);
        }
        printf("Freeing the encryption session.\n");
        free(sess->encrypt);
    }
    printf("Freeing the upload session.\n");
    free(sess->upload->destContainer);
    free(sess->upload);
    free(sess);
}

/*
Open and allocate an unencrypted upload session
*/
struct SESSION *open_session_unenc(
    const char *uploadIdStr,
    const char *destContainer)
{
    struct SESSION *ret = malloc(sizeof(struct SESSION));
    ret->upload = malloc(sizeof(struct UPLOAD_SESSION));
    ret->encrypt = NULL;
    ret->upload->destContainer = malloc(strlen(destContainer + 1));
    strcpy(ret->upload->destContainer, destContainer);
    strcpy(ret->upload->uploadIdStr, uploadIdStr);
    return ret;
}
