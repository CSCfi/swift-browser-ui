#include "unity.h"
#include <stdlib.h>
#include <stdint.h>
#include "mock_stub_sodium.h"
#include "mock_stub_crypt4gh.h"
#include "mock_stub_unistd.h"
#include "mock_stub_ftw.h"
#include "upcommon.h"
#include "uptypes.h"

void setUp() {}
void tearDown() {}

void test_create_keypair_should_return_a_keypair(void)
{
    crypto_kx_keypair_ExpectAnyArgs();

    KEYPAIR *ret = create_keypair();

    TEST_ASSERT_NOT_EQUAL(ret, NULL);
    free(ret);
}

void test_free_keypair_should_succeed(void)
{
    KEYPAIR *t = calloc(sizeof(KEYPAIR), 1);
    free_keypair(t);
}

void test_get_keypair_public_key_should_return_public_key(void)
{
    KEYPAIR *kp = calloc(sizeof(KEYPAIR), 1);

    void *ret = get_keypair_public_key(kp);

    TEST_ASSERT_EQUAL(ret, kp->public);
    free(kp);
}

void test_get_keypair_private_key_should_return_private_key(void)
{
    KEYPAIR *kp = calloc(sizeof(KEYPAIR), 1);

    void *ret = get_keypair_private_key(kp);

    TEST_ASSERT_EQUAL(ret, kp->private);
    free(kp);
}

void test_crypt4gh_session_key_new_should_fail_with_failed_sodium_init(void)
{
    sodium_init_ExpectAndReturn(-1);
    uint8_t *ret = crypt4gh_session_key_new();
    TEST_ASSERT_EQUAL(ret, NULL);
}

void test_crypt4gh_session_key_new_should_fail_with_failed_key_creation(void)
{
    sodium_init_ExpectAndReturn(0);
    sodium_malloc_ExpectAndReturn(CRYPT4GH_SESSION_KEY_SIZE * sizeof(uint8_t), NULL);
    uint8_t *ret = crypt4gh_session_key_new();
    TEST_ASSERT_EQUAL(ret, NULL);
}

void test_crypt4gh_session_key_new_should_return_new_key(void)
{
    uint8_t *tp = calloc(sizeof(uint8_t), CRYPT4GH_SESSION_KEY_SIZE);

    sodium_init_ExpectAndReturn(0);
    sodium_malloc_ExpectAndReturn(CRYPT4GH_SESSION_KEY_SIZE * sizeof(uint8_t), tp);
    randombytes_buf_Expect(tp, CRYPT4GH_SESSION_KEY_SIZE);
    sodium_mprotect_readonly_Expect(tp);

    uint8_t *ret = crypt4gh_session_key_new();
    TEST_ASSERT_EQUAL(ret, tp);
}

void test_free_crypt4gh_session_key_should_call_sodium_free(void)
{
    sodium_free_Expect(NULL);
    free_crypt4gh_session_key(NULL);
}

void test_nftwremove_should_call_unlink_for_files(void)
{
    unsigned char tpath[10] = "test-path";
    unlink_ExpectAndReturn(tpath, 1);
    int ret = nftwremove(tpath, NULL, 2, NULL);
    TEST_ASSERT(ret);
}

void test_nftwremove_should_ignore_other_than_files(void)
{
    unsigned char tpath[10] = "test-path";
    int ret = nftwremove(tpath, NULL, 0, NULL);
    TEST_ASSERT(!ret);
}

void test_rmrecv_should_call_nftw(void)
{
    unsigned char tpath[10] = "test-path";
    nftw_ExpectAndReturn(tpath, &nftwremove, 5, 0, 0);
    int ret = rmrecv(tpath);
    TEST_ASSERT(!ret);
}

void test_allocate_chunk_should_return_chunk(void) {
    CHUNK *ret = allocate_chunk();
    TEST_ASSERT_NOT_EQUAL(ret, NULL);
    TEST_ASSERT_EQUAL(ret->chunk, NULL);
    TEST_ASSERT_EQUAL(ret->len, 0);
}

void test_wrap_chunk_len_should_return_chunk_len(void) {
    CHUNK *ret = allocate_chunk();
    ret->len = 15;
    int val = wrap_chunk_len(ret);
    TEST_ASSERT_EQUAL(val, 15);
}

void test_wrap_chunk_content_should_return_chunk_content(void) {
    CHUNK *ret = allocate_chunk();
    uint8_t *val = wrap_chunk_content(ret);
    TEST_ASSERT_EQUAL(val, NULL);
}

void test_free_chunk_should_succeed(void) {
    CHUNK *ret = allocate_chunk();
    free_chunk(ret);
}
