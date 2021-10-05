/*
Init functions for folder upload
*/

#include <unistd.h>
#include <fcntl.h>
#include <sodium.h>
#include <ftw.h>
#include <string.h>
#include <crypt4gh/key.h>
#include <uuid/uuid.h>

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
    int ftype,
    struct FTW *ftw)
{
    // We'll use a 1024 byte buffer, enough for both ed25519 ssh and
    // c4gh keys.
    char *fout = malloc(1024);
    unsigned char pub[crypto_kx_PUBLICKEYBYTES];
    int fd;
    int amount;

    switch (ftype)
    {
    case FTW_F:
        fd = open(path, O_RDONLY);
        amount = read(fd, fout, 1024);
        // Skip if couldn't read from the file or current session is NULL
        if (amount <= 0 || !current)
        {
            goto finalAddRecv;
        }
        // Reuse amount for pubkey return value
        amount = crypt4gh_public_key_from_blob(
            fout,
            amount,
            pub);
        if (amount)
        {
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
        current->recv_key_amount++;
        break;
    // Ignore everything other than ordinary files
    default:
        break;
    }
finalAddRecv:
    free(fout);
    close(fd);
    return 0;
}

/*
Read in the keys for upload encryption
*/
int read_in_keys(
    const struct UPLOAD_SESSION *resumableSession,
    struct ENCRYPT_SESSION *sess)
{
    chdir(resumableSession->resumableIdStr);
    // Read in the private key
    // We assume current working directory to be of the correct structure
    // JS side takes care of that
    char *passphrase = malloc(1024); // KiB buffer should be enough for a passphrase
    scanf("%1023s", passphrase);
    crypt4gh_private_key_from_file(
        "keys/pk.key",
        passphrase,
        sess->seckey,
        sess->pubkey);
    // Read in the receiving keys
    current = sess;
    ftw(
        "data",
        add_recv_key,
        5 // using at most 5 file descriptors for now
    );
finalReadIn:
    current = NULL;
    free(passphrase);
    chdir("..");
}

/*
Open and allocate an upload session
*/
struct SESSION *open_session(
    const char *resumableId,
    const char *destContainer)
{
    struct SESSION *ret = malloc(sizeof(struct SESSION));
    // Allocate encrypt and upload sessions
    ret->upload = malloc(sizeof(struct UPLOAD_SESSION));
    ret->encrypt = malloc(sizeof(struct ENCRYPT_SESSION));
    // Initialize the sessions
    ret->upload->destContainer = malloc(strlen(destContainer));
    strcpy(ret->upload->destContainer, destContainer);
    strcpy(ret->upload->resumableIdStr, resumableId);
    ret->encrypt->recv_keys = NULL;
    ret->encrypt->recv_key_amount = 0;
    return ret;
}

/*
Close and free an upload session
*/
void close_session(
    struct SESSION *sess)
{
    if (sess->encrypt->recv_keys)
    {
        free(sess->encrypt->recv_keys);
    }
    free(sess->upload->destContainer);
    free(sess->encrypt);
    free(sess->upload);
    free(sess);
}
