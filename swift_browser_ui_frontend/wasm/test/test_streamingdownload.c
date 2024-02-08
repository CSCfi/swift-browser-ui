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
#include "streamingdownload.h"

void setUp(void) {}
void tearDown(void) {}

void test_get_session_key_from_header_should_call_header_parse_and_return_null_with_no_keys(void)
{
    char header[10] = "test-path";
    KEYPAIR kp;

    open_ExpectAndReturn(header, 1, 0);
    crypt4gh_header_parse_ExpectAndReturn(0, kp.private, kp.public, NULL, NULL, NULL, NULL, 0);
    crypt4gh_header_parse_IgnoreArg_keys();
    crypt4gh_header_parse_IgnoreArg_nkeys();
    crypt4gh_header_parse_IgnoreArg_edit_list();
    crypt4gh_header_parse_IgnoreArg_edit_list_len();

    uint8_t *ret = get_session_key_from_header(&kp, header);
    TEST_ASSERT_EQUAL(ret, NULL);
}

void test_decrypt_chunk_should_allocate_chunk_and_call_segment_decrypt(void)
{
    uint8_t session_key[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    uint8_t segment[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    unsigned long int len_segment = 10;
    CHUNK c;

    allocate_chunk_ExpectAndReturn(&c);
    crypt4gh_segment_decrypt_ExpectAndReturn(session_key, segment, len_segment, NULL, NULL, 0);
    crypt4gh_segment_decrypt_IgnoreArg_chunk();
    crypt4gh_segment_decrypt_IgnoreArg_len_chunk();

    CHUNK *ret = decrypt_chunk(session_key, segment, len_segment);
    TEST_ASSERT(ret);
    TEST_ASSERT_NOT_EQUAL(ret->chunk, NULL);
    TEST_ASSERT_EQUAL(&c, ret);
}
