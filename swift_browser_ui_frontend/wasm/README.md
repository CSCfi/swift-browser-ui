# Upload encryption based on crypt4gh using libcrypt4gh

## Implementation details
In order to keep the C side of things as simple as possible, we assume the
correct directory structure to always be in place when the upload loop is run.
The filenames are also kept constant – JS side is relied upon to copy the
correct private etc. keys to the filesystem from browser storage.

The directory structure is as follows:

* keys
    * pk.key
    * recv_keys
        * pub_key_0
        * pub_key_1
        * pub_key_2
        * ...
        * pub_key_n
* data
    * data_0
    * data_1
    * data_f
        * data_2
        * data_3
    * data_4
    * ...
    * data_n

The `recv_keys` file is simply a folder that contains multiple files, all of
them being public keys to encrypt for.

The `data` folder will be the folder that is to be uploaded.

The constant filenames are  `keys`, `data`, `keys/pk.key` and `keys/recv_keys`.

Other than this the filenames are free to choose from.
