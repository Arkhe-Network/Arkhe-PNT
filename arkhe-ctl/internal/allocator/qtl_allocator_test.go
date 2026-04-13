package allocator

import (
	"testing"
	"unsafe"
)

func TestQTLAllocatorAlignment(t *testing.T) {
	alignment := 64
	alloc := NewQTLAllocator(1024*1024, alignment)

	for i := 0; i < 100; i++ {
		ptr, err := alloc.Allocate(8)
		if err != nil {
			t.Fatal(err)
		}

		addr := uintptr(ptr)
		if addr == 0 {
			t.Fatal("pointer is nil")
		}
		if addr%uintptr(alignment) != 0 {
			t.Errorf("Allocation %d not aligned: %x %% %x != 0", i, addr, alignment)
		}
	}
	t.Log(alloc.Stats())
}

func TestQTLAllocatorFragmentation(t *testing.T) {
	alloc := NewQTLAllocator(4096, 8)

	for i := 0; i < 500; i++ {
		ptr, err := alloc.Allocate(8)
		if err != nil {
			t.Fatal(err)
		}
		if ptr == nil {
			t.Fatal("Allocation failed")
		}
	}

	t.Log(alloc.Stats())
}

// Dummy use to prevent "imported and not used" error
var _ unsafe.Pointer
