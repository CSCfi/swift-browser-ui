#include "unity.h"
#include <stdint.h>
#include <stdlib.h>
#include "mock_stub_crypt4gh_header.h"
#include "mock_stub_crypt4gh_segment.h"
#include "mock_stub_crypt4gh.h"
#include "mock_stub_sodium.h"
#include "mock_stub_unistd.h"
#include "mock_upcommon.h"
#include "uptypes.h"
#include "streamingupload.h"

void setUp(void) {}
void tearDown(void) {}

void test_create_session_key_should_return_key_pointer(void)
{
    crypt4gh_session_key_new_ExpectAndReturn(NULL);
    uint8_t *ret = create_session_key();
    TEST_ASSERT_EQUAL(ret, NULL);
}

void test_create_crypt4gh_header_should_allocate_chunk_and_call_header_build(void)
{
    CHUNK c;
    uint8_t session_key = 1;
    uint8_t secret_key = 2;
    uint8_t receivers = 3;
    unsigned int len_receivers = 1;

    allocate_chunk_ExpectAndReturn(&c);
    crypt4gh_header_build_ExpectAndReturn(&session_key, &secret_key, &receivers, len_receivers, &(c.chunk), &(c.len), 0);
    CHUNK *ret = create_crypt4gh_header(&session_key, &secret_key, &receivers, len_receivers);
    TEST_ASSERT_EQUAL(ret, &c);
}

void test_encrypt_chunk_should_allocate_chunk_and_call_segment_encrypt(void)
{
    CHUNK c;
    uint8_t session_key = 1;
    uint8_t segment[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    unsigned long int len_segment = 10;

    allocate_chunk_ExpectAndReturn(&c);
    crypt4gh_segment_encrypt_ExpectAndReturn(&session_key, segment, len_segment, NULL, NULL, 0);
    crypt4gh_segment_encrypt_IgnoreArg_chunk();
    crypt4gh_segment_encrypt_IgnoreArg_len_chunk();
    CHUNK *ret = encrypt_chunk(&session_key, segment, len_segment);
    TEST_ASSERT_EQUAL(ret, &c);
    TEST_ASSERT_NOT_EQUAL(ret->chunk, NULL);
    free(ret->chunk);
}
