/*
Definitions of a single folder upload session
*/

#include <ftw.h>

#ifndef SWIFT_UI_UPLOAD_INCLUDED
#define SWIFT_UI_UPLOAD_INCLUDED

/*
Encrypt a single file – function assumes global session and callee being nftw()
*/
int encrypt_file(
    const char *path,
    const struct stat *st,
    int flag,
    struct FTW *ftws);

/*
Encrypt the files inside a path listing.
*/
int encrypt_files(void);

/*
Encrypt a folder using crypt4gh.
*/
int encrypt_folder(char *passphrase);

/*
Encrypt a folder using crypt4gh with ephemeral keys.
*/
int encrypt_folder_ephemeral();

int main(void);
#endif
