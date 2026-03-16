CC = gcc
CFLAGS = -Wall -Wextra -std=c17 -g
TARGET = profiler
TEST_TARGET = test_profiler

all: $(TARGET) $(TEST_TARGET)

$(TARGET): profiler.c
	$(CC) $(CFLAGS) -o $(TARGET) profiler.c

$(TEST_TARGET): test_profiler.c profiler.c
	$(CC) $(CFLAGS) -DTESTING -o $(TEST_TARGET) test_profiler.c

test: $(TEST_TARGET)
	./$(TEST_TARGET)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET) $(TEST_TARGET) *.o trace_output.json

.PHONY: all test run clean
