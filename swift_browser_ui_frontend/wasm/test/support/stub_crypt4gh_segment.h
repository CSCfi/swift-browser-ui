#include <stdint.h>

#ifndef __STUB_CRYPT4GH_SEGMENT
#define __STUB_CRYPT4GH_SEGMENT

int crypt4gh_segment_encrypt(const uint8_t *session_key, uint8_t *segment, unsigned long int len_segment, uint8_t *chunk, unsigned long int *len_chunk);
int crypt4gh_segment_decrypt(const uint8_t *session_key, uint8_t *segment, unsigned long int len_segment, uint8_t *chunk, unsigned long int *len_chunk);

#endif
