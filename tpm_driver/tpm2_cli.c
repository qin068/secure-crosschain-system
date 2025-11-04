#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <readline/readline.h>
#include <readline/history.h>
#include "tpm2_common.h"

void print_banner() {
    printf("\n");
    printf("===================================\n");
    printf("    TPM2 Secure Communication\n");
    printf("===================================\n");
    printf("Commands:\n");
    printf("  listen <port>    - Start listening on port\n");
    printf("  encrypt <data>   - Encrypt data\n");
    printf("  decrypt <data>   - Decrypt data\n");
    printf("  hash <data>      - Calculate hash\n");
    printf("  sign <data>      - Sign data\n");
    printf("  genkey           - Generate new key\n");
    printf("  status           - Show system status\n");
    printf("  quit             - Exit program\n");
    printf("===================================\n\n");
}

void handle_command(tpm2_server_t *server, const char *command) {
    char *cmd = strdup(command);
    char *token = strtok(cmd, " ");
    
    if (!token) {
        free(cmd);
        return;
    }
    
    if (strcmp(token, "listen") == 0) {
        char *port_str = strtok(NULL, " ");
        if (port_str) {
            int port = atoi(port_str);
            printf("Starting listener on port %d...\n", port);
        }
    }
    else if (strcmp(token, "encrypt") == 0) {
        char *data = strtok(NULL, "");
        if (data) {
            printf("Encrypting: %s\n", data);
            // 调用加密函数
        }
    }
    else if (strcmp(token, "decrypt") == 0) {
        char *data = strtok(NULL, "");
        if (data) {
            printf("Decrypting: %s\n", data);
            // 调用解密函数
        }
    }
    else if (strcmp(token, "hash") == 0) {
        char *data = strtok(NULL, "");
        if (data) {
            printf("Calculating hash for: %s\n", data);
            // 调用哈希函数
        }
    }
    else if (strcmp(token, "sign") == 0) {
        char *data = strtok(NULL, "");
        if (data) {
            printf("Signing: %s\n", data);
            // 调用签名函数
        }
    }
    else if (strcmp(token, "genkey") == 0) {
        printf("Generating new RSA key...\n");
        // 调用密钥生成函数
    }
    else if (strcmp(token, "status") == 0) {
        printf("TPM2 Server Status:\n");
        printf("  Running: %s\n", server->running ? "Yes" : "No");
        printf("  TPM Initialized: %s\n", server->esys_context ? "Yes" : "No");
        printf("  Client Connected: %s\n", server->client_connected ? "Yes" : "No");
    }
    else if (strcmp(token, "quit") == 0) {
        printf("Shutting down...\n");
        server->running = 0;
    }
    else {
        printf("Unknown command: %s\n", token);
        printf("Type 'help' for available commands\n");
    }
    
    free(cmd);
}
