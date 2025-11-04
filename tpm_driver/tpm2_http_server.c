// tpm2_http_server.c
#include <microhttpd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "tpm2_common.h"
#include "tpm2_crypto.h"
#include "tpm2_api.h"        // 必须包含！

#define PORT 8080

tpm2_server_t server;

static enum MHD_Result answer_to_connection(
    void *cls, struct MHD_Connection *connection,
    const char *url, const char *method,
    const char *version, const char *upload_data,
    size_t *upload_data_size, void **con_cls)
{
    (void)cls; (void)version; (void)upload_data;
    (void)upload_data_size; (void)con_cls;

    if (strcmp(method, "GET") != 0) return MHD_NO;

    char *response = NULL;
    int status_code = 200;

    if (strcmp(url, "/status") == 0) {
        response = malloc(512);
        if (!response) return MHD_NO;
        snprintf(response, 512,
                 "{"
                 "\"tpm_available\": %s,"
                 "\"running\": true,"
                 "\"timestamp\": %ld"
                 "}",
                 server.esys_context ? "true" : "false", time(NULL));
    }
    else if (strcmp(url, "/genkey") == 0) {
        if (!server.esys_context) {
            response = strdup("{\"error\": \"TPM not available\"}");
            status_code = 500;
        } else {
            ESYS_TR key_handle = ESYS_TR_NONE;
            if (generate_rsa_key(server.esys_context, &key_handle) == 0) {
                response = malloc(256);
                if (response) {
                    snprintf(response, 256,
                             "{\"status\": \"key_generated\", \"handle\": %u}",
                             key_handle);
                }
            } else {
                response = strdup("{\"error\": \"key generation failed\"}");
                status_code = 500;
            }
        }
    }
    else {
        response = strdup("{\"error\": \"Not found\"}");
        status_code = 404;
    }

    if (!response) return MHD_NO;

    struct MHD_Response *mhd_response = MHD_create_response_from_buffer(
        strlen(response), (void *)response, MHD_RESPMEM_MUST_FREE);

    MHD_add_response_header(mhd_response, "Content-Type", "application/json");
    enum MHD_Result ret = MHD_queue_response(connection, status_code, mhd_response);
    MHD_destroy_response(mhd_response);
    return ret;
}

int main() {
    memset(&server, 0, sizeof(server));

    if (initialize_tpm(&server) != 0) {
        fprintf(stderr, "TPM init failed, running in limited mode\n");
        server.esys_context = NULL;
    } else {
        printf("TPM2.0 initialized successfully\n");
    }

    struct MHD_Daemon *daemon = MHD_start_daemon(
        MHD_USE_SELECT_INTERNALLY, PORT, NULL, NULL,
        &answer_to_connection, NULL, MHD_OPTION_END);

    if (!daemon) {
        fprintf(stderr, "Failed to start HTTP server on port %d\n", PORT);
        cleanup(&server);
        return 1;
    }

    printf("TPM2 HTTP Server running on http://localhost:8080\n");
    printf("Endpoints: /status, /genkey\n");
    printf("Server will run forever. Use 'kill' to stop.\n");

    // 永久运行，不等待输入
    while (1) {
        sleep(1);
    }

    // 永远不会执行到这里
    MHD_stop_daemon(daemon);
    cleanup(&server);
    return 0;
}
