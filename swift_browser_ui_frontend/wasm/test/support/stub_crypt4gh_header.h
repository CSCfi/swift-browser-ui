#ifndef __STUB_CRYPT4GH_HEADER
#define __STUB_CRYPT4GH_HEADER
#include <stdint.h>

int crypt4gh_header_build(const uint8_t *, const uint8_t *, const uint8_t *, const unsigned int, uint8_t *, long unsigned int);
int crypt4gh_header_parse(const int fd, const uint8_t *private_key, const uint8_t *public_key, uint8_t **keys, unsigned long int *nkeys, uint8_t **edit_list, unsigned long int *edit_list_len);

#endif
