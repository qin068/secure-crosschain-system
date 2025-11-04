// tpm2_api.h
#ifndef TPM2_API_H
#define TPM2_API_H

#include "tpm2_common.h"

// 声明从 tpm2_secure_comms.c 来的函数
int initialize_tpm(tpm2_server_t *server);
int generate_rsa_key(ESYS_CONTEXT *ctx, ESYS_TR *key_handle);
void cleanup(tpm2_server_t *server);

#endif
