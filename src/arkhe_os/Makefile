CC=gcc
CFLAGS=-Wall -fPIC -shared -ldl -lm
TARGET=libarkhe_alloc.so

all: $(TARGET)

$(TARGET): arkhe_alloc.c
	$(CC) $(CFLAGS) -o $(TARGET) arkhe_alloc.c

clean:
	rm -f $(TARGET)

inject: $(TARGET)
	@echo "🜏 Injecting Arkhe Allocator into shell..."
	@echo "Run your commands with: LD_PRELOAD=./$(TARGET) <command>"
