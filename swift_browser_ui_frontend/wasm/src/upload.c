/*
Init function for folder upload
*/

#define _XOPEN_SOURCE 500

#include <unistd.h>
#include <fcntl.h>
#include <sodium.h>
#include <ftw.h>
#include <string.h>

#include <crypt4gh.h>

#include "include/uptypes.h"
#include "include/upinit.h"

#include "include/upload.h"

/*
Using global variable scope for the key variables to enable using them
inside the `encrypt_file` function. Without global scope would need to pass
the keys inside ftw.
*/
struct SESSION *sess = NULL;

int encrypt_file(
    const char *path,
    const struct stat *st,
    int flag)
{
    int fd_in = 0;
    int fd_out = 0;
    int ret = 0;

    char *fname_out = malloc(strlen(path) + 6);
    strncpy(fname_out, path, strlen(path));
    strcat(fname_out, ".c4gh");

    // Encrypt a single file
    if (flag == FTW_F)
    {
        fd_in = open(path, O_RDONLY);
        fd_out = creat(fname_out, 0b110110110); // create output file with a+rw
        if (!fd_in || !fd_out)
        {
            goto finalEncFile;
        }
        ret = crypt4gh_encrypt(
            fd_in,
            fd_out,
            sess->encrypt->seckey,
            sess->encrypt->pubkey,
            sess->encrypt->recv_keys,
            sess->encrypt->recv_key_amount);
    }
finalEncFile:
    if (fd_in)
        close(fd_out);
    if (fd_out)
        close(fd_out);
    // Delete the source file if encryption was successful
    if (!ret)
    {
        remove(path);
    }
    free(fname_out);
    return ret;
}

/*
Encrypt the files inside a path listing.
*/
int encrypt_files(void)
{
    chdir(sess->upload->uploadIdStr);
    if (!sess)
    {
        return 1;
    }
    return nftw(
        "data",
        encrypt_file,
        5, // using at most 5 file descriptors
        FTW_PHYS);
}

/*
Encrypt a folder using crypt4gh.
*/
int encrypt_folder(void)
{
    int ret = 0;
    sess = open_session_enc("placeholder", "placeholder");

    ret = read_in_keys(
        sess->upload,
        sess->encrypt);
    if (ret)
    {
        goto final_eup;
    }

    ret = encrypt_files();
    if (ret)
    {
        goto final_eup;
    }
final_eup:
    if (sess)
    {
        close_session(sess);
    }
    sess = NULL;
    return ret;
}

// int main(void)
// {
//     return encrypt_folder();
// }
