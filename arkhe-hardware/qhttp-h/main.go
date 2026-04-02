package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

// ConsensusState represents the health of the Arkhe network
type ConsensusState struct {
	Sigma float64 `json:"sigma"`
}

// HardwareDriver simulates the GPIO interface for the qhttp-H wearable
type HardwareDriver struct {
	VibrationMotorPin int
	LedRedPin         int
	LedGreenPin       int
	LedYellowPin      int
}

func NewHardwareDriver() *HardwareDriver {
	log.Println("Initializing qhttp-H hardware driver...")
	return &HardwareDriver{
		VibrationMotorPin: 18,
		LedRedPin:         23,
		LedGreenPin:       24,
		LedYellowPin:      25,
	}
}

// SetVibration controls the haptic feedback motor
func (hw *HardwareDriver) SetVibration(active bool, intensity int) {
	if active {
		log.Printf("[qhttp-H] 📳 VIBRATION MOTOR ON (Intensity: %d%%)", intensity)
	} else {
		log.Println("[qhttp-H] 📴 VIBRATION MOTOR OFF")
	}
}

// SetLED controls the RGB/Status LEDs
func (hw *HardwareDriver) SetLED(color string, blink bool) {
	state := "SOLID"
	if blink {
		state = "BLINKING"
	}
	log.Printf("[qhttp-H] 💡 LED STATUS: %s (%s)", color, state)
}

// FetchConsensusState polls the Arkhe Oracle/Sentinel for the current Sigma value
func FetchConsensusState(endpoint string) (*ConsensusState, error) {
	// In a real scenario, this would hit the Arkhe Oracle API
	// For simulation, we'll mock the response based on a local endpoint or return a default
	resp, err := http.Get(endpoint)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var state ConsensusState
	if err := json.NewDecoder(resp.Body).Decode(&state); err != nil {
		return nil, err
	}
	return &state, nil
}

func main() {
	log.Println("🜏 Starting Arkhe qhttp-H Wearable Daemon 🜏")
	
	hw := NewHardwareDriver()
	
	// Graceful shutdown
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-c
		log.Println("Shutting down qhttp-H daemon...")
		hw.SetVibration(false, 0)
		hw.SetLED("OFF", false)
		os.Exit(0)
	}()

	// Mock endpoint for the Oracle
	oracleEndpoint := os.Getenv("ARKHE_ORACLE_URL")
	if oracleEndpoint == "" {
		oracleEndpoint = "http://localhost:3000/api/consensus"
	}

	// Main sensory loop
	for {
		state, err := FetchConsensusState(oracleEndpoint)
		
		sigma := 1.0 // Default to healthy if unreachable
		if err == nil && state != nil {
			sigma = state.Sigma
		} else {
			log.Printf("Warning: Could not fetch consensus state: %v. Assuming default.", err)
			// Simulate a drop in coherence for testing if the server is offline
			sigma = 0.65 
		}

		// Apply hardware feedback based on Sigma (Coherence)
		if sigma > 0.90 {
			// Healthy
			hw.SetLED("GREEN", false)
			hw.SetVibration(false, 0)
		} else if sigma > 0.75 {
			// Warning: Entropy Detected
			hw.SetLED("YELLOW", true)
			hw.SetVibration(true, 30) // Light vibration
			time.Sleep(500 * time.Millisecond)
			hw.SetVibration(false, 0)
		} else {
			// Critical: Reorg Imminent / Consensus Failure
			hw.SetLED("RED", true)
			hw.SetVibration(true, 100) // Strong haptic feedback
			log.Println("🚨 CRITICAL: Haptic feedback triggered due to severe decoherence!")
		}

		time.Sleep(5 * time.Second) // Poll every 5 seconds
	}
}
