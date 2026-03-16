CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17 -g
TARGET = nine_slice
TEST_TARGET = test_nine_slice

all: $(TARGET) $(TEST_TARGET)

$(TARGET): nine_slice.cpp nine_slice.hpp
	$(CXX) $(CXXFLAGS) -o $(TARGET) nine_slice.cpp

$(TEST_TARGET): test_nine_slice.cpp nine_slice.cpp nine_slice.hpp
	$(CXX) $(CXXFLAGS) -DTESTING -o $(TEST_TARGET) test_nine_slice.cpp

test: $(TEST_TARGET)
	./$(TEST_TARGET)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET) $(TEST_TARGET) *.o

.PHONY: all test run clean
