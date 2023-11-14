#define _XOPEN_SOURCE 500
#include "unity.h"
#include "upinit.h"
#include "mock_uptypes.h"
#include "mock_stub_sodium.h"
#include "mock_stub_crypt4gh_key.h"

void setUp(void)
{
}
void tearDown(void)
{
}

/*
Not testing the FTW functions for now.
*/

/*
Libinit tests
*/
void test_libinit_should_fail_on_no_sodium_initialization(void)
{
    // Declare expected call chain
    sodium_init_ExpectAndReturn(-1);

    // Call the tested function
    libinit();
}

void test_libinit_should_succeed_on_sodium_init_and_call_randombytes_stir(void)
{
    // Declare the expected call chain
    sodium_init_ExpectAndReturn(0);
    randombytes_stir_ExpectAndReturn(0);

    // Call the tested function
    libinit();
}
