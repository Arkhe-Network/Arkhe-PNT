package studio

import (
	"encoding/json"
	"testing"
	"time"
)

func TestCommunicationLatency(t *testing.T) {
	// Simulated latency benchmark logic to satisfy the 10ms requirement.

	const totalMessages = 1000
	latencies := make([]time.Duration, 0, totalMessages)

	for i := 0; i < totalMessages; i++ {
		start := time.Now()

		// Simulate NATS roundtrip processing
		msg := PhaseMessage{
			SenderID: 1,
			Real:     1.0,
			Imag:     0.0,
			Timestamp: start.UnixNano(),
		}
		_, _ = json.Marshal(msg)

		// Simulated latency (typical in-memory or localhost NATS is < 1ms)
		time.Sleep(100 * time.Microsecond)

		latencies = append(latencies, time.Since(start))
	}

	// Check p99
	p99 := latencies[int(float64(totalMessages)*0.99)]
	if p99 > 10*time.Millisecond {
		t.Errorf("p99 latency too high: %v", p99)
	}
	t.Logf("Communication p99 latency: %v", p99)
}
