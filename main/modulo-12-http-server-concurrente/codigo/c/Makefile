# Makefile — Módulo 12: Servidor HTTP Concurrente en C
#
# Targets:
#   make           → Compila el servidor ejecutable
#   make test      → Compila y ejecuta los tests unitarios
#   make clean     → Elimina binarios generados

CC      = gcc
CFLAGS  = -Wall -Wextra -Wpedantic -O2 -std=c11
LDFLAGS = -lpthread

# Nombre del ejecutable del servidor
SERVER  = http_server
# Nombre del ejecutable de tests
TEST    = test_http_server

.PHONY: all test clean

all: $(SERVER)

# Compilar el servidor como ejecutable (con main())
$(SERVER): http_server.c http_server.h
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

# Compilar los tests (http_server.c en modo librería, sin main())
$(TEST): test_http_server.c http_server.c http_server.h
	$(CC) $(CFLAGS) -DHTTP_SERVER_LIBRARY_MODE -o $@ \
		test_http_server.c http_server.c $(LDFLAGS)

# Compilar y ejecutar los tests
test: $(TEST)
	./$(TEST)

clean:
	rm -f $(SERVER) $(TEST)
