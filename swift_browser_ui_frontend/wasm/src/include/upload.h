/*
Definitions of a single folder upload session
*/

#include <ftw.h>

#ifndef SWIFT_UI_UPLOAD_INCLUDED
#define SWIFT_UI_UPLOAD_INCLUDED

int encrypt_file(
    const char *path,
    const struct stat *st,
    int flag,
    struct FTW *ftws);

int encrypt_files(void);

int encrypt_folder(void);

int main(void);
#endif
