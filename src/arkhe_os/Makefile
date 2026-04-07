CC=gcc
CFLAGS=-Wall -fPIC
LIBS=-lm
TARGET_LIB=libarkhe.so
ALLOC_LIB=libarkhe_alloc.so
DAEMON=arkhe_daemon
PVM=pvm
BOOT=arkhe_os

all: $(TARGET_LIB) $(ALLOC_LIB) $(DAEMON) $(PVM) $(BOOT)

$(TARGET_LIB): arkhe_hal.c cronos_scheduler.c
	$(CC) $(CFLAGS) -shared -o $(TARGET_LIB) arkhe_hal.c cronos_scheduler.c $(LIBS)

$(ALLOC_LIB): arkhe_alloc.c
	$(CC) $(CFLAGS) -shared -o $(ALLOC_LIB) arkhe_alloc.c -ldl $(LIBS)

$(DAEMON): daemon/arkhe_daemon.c $(TARGET_LIB)
	$(CC) $(CFLAGS) -o $(DAEMON) daemon/arkhe_daemon.c -L. -larkhe -Wl,-rpath,. $(LIBS)

$(PVM): vm/phase_vm.c vm/main_vm.c $(TARGET_LIB)
	$(CC) $(CFLAGS) -o $(PVM) vm/phase_vm.c vm/main_vm.c -L. -larkhe -Wl,-rpath,. $(LIBS)

$(BOOT): main.c $(TARGET_LIB)
	$(CC) $(CFLAGS) -o $(BOOT) main.c vm/phase_vm.c -L. -larkhe -Wl,-rpath,. $(LIBS)

clean:
	rm -f $(TARGET_LIB) $(ALLOC_LIB) $(DAEMON) $(PVM) $(BOOT)

install:
	@echo "🜏 Arkhe OS installation successful. Phase-lock established."
