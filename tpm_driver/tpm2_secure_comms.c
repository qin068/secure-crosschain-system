#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <tss2/tss2_esys.h>
#include <tss2/tss2_tcti_device.h>
#include <readline/readline.h>    // 添加这行
#include <readline/history.h>     // 添加这行
#include "tpm2_common.h"
#include "tpm2_crypto.h"

// TPM2初始化
int initialize_tpm(tpm2_server_t *server) {
    TSS2_RC rc;
    TSS2_TCTI_CONTEXT *tcti_context = NULL;
    size_t size;
    
    printf("Initializing TPM2.0...\n");
    
    // 初始化TCTI
    rc = Tss2_Tcti_Device_Init(NULL, &size, NULL);
    if (rc != TSS2_RC_SUCCESS) {
        printf("Failed to get TCTI device size: 0x%x\n", rc);
        return -1;
    }
    
    tcti_context = (TSS2_TCTI_CONTEXT*)calloc(1, size);
    if (!tcti_context) {
        printf("Memory allocation failed\n");
        return -1;
    }
    
    rc = Tss2_Tcti_Device_Init(tcti_context, &size, DEVICE_PATH);
    if (rc != TSS2_RC_SUCCESS) {
        printf("Failed to initialize TCTI: 0x%x\n", rc);
        free(tcti_context);
        return -1;
    }
    
    // 初始化ESAPI
    rc = Esys_Initialize(&server->esys_context, tcti_context, NULL);
    if (rc != TSS2_RC_SUCCESS) {
        printf("Failed to initialize ESAPI: 0x%x\n", rc);
        free(tcti_context);
        return -1;
    }
    
    printf("TPM2.0 initialized successfully\n");
    return 0;
}

// 生成RSA密钥（简化版本）
int generate_rsa_key(ESYS_CONTEXT *ctx, ESYS_TR *key_handle) {
    (void)ctx;  // 标记未使用参数
    
    printf("Key generation function placeholder\n");
    *key_handle = ESYS_TR_NONE;
    return 0;
}

// 清理资源
void cleanup(tpm2_server_t *server) {
    printf("Cleaning up resources...\n");
    if (server->esys_context) {
        Esys_Finalize(&server->esys_context);
        server->esys_context = NULL;
    }
}

// 信号处理
void signal_handler(int sig) {
    printf("\nReceived signal %d, shutting down...\n", sig);
    exit(0);
}

// 打印状态信息
void print_status(tpm2_server_t *server) {
    printf("=== TPM2 Server Status ===\n");
    printf("Running: %s\n", server->running ? "Yes" : "No");
    printf("TPM Context: %p\n", (void*)server->esys_context);
    printf("TPM Available: %s\n", server->esys_context ? "Yes" : "No");
    printf("Client Connected: %s\n", server->client_connected ? "Yes" : "No");
    printf("===========================\n");
}
