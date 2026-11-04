#ifndef __STUB_FTW
#define __STUB_FTW

#define FTW_PHYS 1
#define FTW_F 2
typedef struct FTW
{
} FTW;
typedef struct stat
{
} stat;

typedef int (*nftw_function_ptr)(const char *, const struct stat *, int, struct FTW *);

int nftw(const char *, nftw_function_ptr, int, int);

#endif // __STUB_FTW
