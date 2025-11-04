// tpm2_crypto.h
#ifndef TPM2_CRYPTO_H
#define TPM2_CRYPTO_H

#include <tss2/tss2_esys.h>

// 加密操作
int tpm2_encrypt_data(ESYS_CONTEXT *ctx, ESYS_TR key_handle, 
                      const uint8_t *plaintext, size_t plaintext_len,
                      uint8_t **ciphertext, size_t *ciphertext_len);

// 解密操作
int tpm2_decrypt_data(ESYS_CONTEXT *ctx, ESYS_TR key_handle,
                      const uint8_t *ciphertext, size_t ciphertext_len,
                      uint8_t **plaintext, size_t *plaintext_len);

// 哈希计算
int tpm2_calculate_hash(ESYS_CONTEXT *ctx, const uint8_t *data, size_t data_len,
                        uint8_t *hash, size_t *hash_len);

// 数字签名
int tpm2_sign_data(ESYS_CONTEXT *ctx, ESYS_TR key_handle,
                   const uint8_t *data, size_t data_len,
                   uint8_t **signature, size_t *signature_len);

#endif
