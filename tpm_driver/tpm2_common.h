#ifndef TPM2_COMMON_H
#define TPM2_COMMON_H

#include <tss2/tss2_esys.h>
#include <pthread.h>

#define MAX_BUFFER_SIZE 4096
#define DEVICE_PATH "/dev/tpmrm0"

typedef struct {
    int running;
    int client_connected;
    ESYS_CONTEXT *esys_context;
    pthread_t listen_thread;
    pthread_t crypto_thread;
} tpm2_server_t;

#endif
