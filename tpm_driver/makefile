CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -D_DEFAULT_SOURCE
LDFLAGS = -ltss2-esys -ltss2-tcti-device -lreadline -lpthread -lmicrohttpd
TARGET = tpm2-http-server
SOURCES = tpm2_http_server.c tpm2_secure_comms.c tpm2_crypto.c

all: $(TARGET)

$(TARGET): $(SOURCES) tpm2_api.h
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCES) $(LDFLAGS)

clean:
	rm -f $(TARGET) *.o

.PHONY: all clean
