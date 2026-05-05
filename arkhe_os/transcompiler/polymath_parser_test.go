package arkhe

import (
	"strings"
	"testing"
)

func TestPolymathParser(t *testing.T) {
	parser := NewPolymathParser()

	// Test case 1: Python to Go
	pythonSource := `
class QuantumSensor:
    def __init__(self):
        self.coherence = 0.95

    async def read(self):
        return {"coherence": self.coherence}

def main():
    sensor = QuantumSensor()
    print("Initializing...")
`
	goCode, err := parser.Transpile(pythonSource, "python", "go")
	if err != nil {
		t.Fatalf("Failed to transpile Python to Go: %v", err)
	}
	if !strings.Contains(goCode, "type QuantumSensor struct") {
		t.Errorf("Expected 'type QuantumSensor struct', got:\n%s", goCode)
	}
	if !strings.Contains(goCode, "func Read()") {
		t.Errorf("Expected 'func Read()', got:\n%s", goCode)
	}

	// Test case 2: Go to Rust
	goSource := `
package main

type SensorData struct {
	Coherence float64
}

func ProcessData() {
	// Processing...
}
`
	rustCode, err := parser.Transpile(goSource, "go", "rust")
	if err != nil {
		t.Fatalf("Failed to transpile Go to Rust: %v", err)
	}
	if !strings.Contains(rustCode, "pub struct SensorData") {
		t.Errorf("Expected 'pub struct SensorData', got:\n%s", rustCode)
	}
	if !strings.Contains(rustCode, "pub fn process_data()") {
		t.Errorf("Expected 'pub fn process_data()', got:\n%s", rustCode)
	}

	// Verify metrics
	health := parser.GetHealth()
	metrics := health["metrics"].(PolymathMetrics)
	if metrics.SuccessfulTranspiles != 2 {
		t.Errorf("Expected 2 successful transpiles, got %d", metrics.SuccessfulTranspiles)
	}
}

func TestSelfHealingOrchestrator(t *testing.T) {
	parser := NewPolymathParser()
	ipfs := &IPFSDeployer{}
	healer := NewSelfHealingOrchestrator(parser, ipfs)

	// Test healing for a RISC-V target (should transpile to Go)
	code, err := healer.HealModule("QmTest123", "python", "riscv64")
	if err != nil {
		t.Fatalf("Failed to heal module: %v", err)
	}
	if !strings.Contains(code, "package generated") {
		t.Errorf("Expected generated Go code, got:\n%s", code)
	}

	// Test healing for an ARM64 target (should transpile to Rust)
	code, err = healer.HealModule("QmTest456", "python", "arm64")
	if err != nil {
		t.Fatalf("Failed to heal module: %v", err)
	}
	if !strings.Contains(code, "pub struct QuantumSensor") {
		t.Errorf("Expected generated Rust code, got:\n%s", code)
	}

	health := healer.GetHealth()
	if health["healings_successful"].(int64) != 2 {
		t.Errorf("Expected 2 successful healings, got %d", health["healings_successful"])
	}
}
