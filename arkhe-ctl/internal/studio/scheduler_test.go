package studio

import (
	"math/cmplx"
	"testing"
	"time"
)

func TestKuramotoFeedbackLatency(t *testing.T) {
	// Setup 75 nodes
	nodes := make([]*CooperNode, 75)
	for i := 0; i < 75; i++ {
		nodes[i] = &CooperNode{
			ID:    i,
			Phase: cmplx.Exp(complex(0, float64(i)*0.1)),
			Omega: 1.0,
		}
	}

	scheduler := NewKuramotoScheduler(nodes)

	// Measure feedback loop latency
	start := time.Now()

	// Measurement + Coupling Adjustment + Step
	scheduler.Step(0.01)

	latency := time.Since(start)
	if latency > 1*time.Millisecond {
		t.Errorf("Feedback loop latency too high: %v", latency)
	}
	t.Logf("Kuramoto feedback latency: %v", latency)
}

func TestKuramotoConvergence(t *testing.T) {
	nodes := make([]*CooperNode, 75)
	for i := 0; i < 75; i++ {
		nodes[i] = &CooperNode{
			ID:    i,
			Phase: cmplx.Exp(complex(0, float64(i)*0.5)), // Highly dispersed
			Omega: 0.1,
		}
	}

	scheduler := NewKuramotoScheduler(nodes)

	initialR, _ := scheduler.CalculateOrderParameter()
	t.Logf("Initial R: %v", initialR)

	// Run many steps
	for i := 0; i < 1000; i++ {
		scheduler.Step(0.1)
	}

	finalR, _ := scheduler.CalculateOrderParameter()
	t.Logf("Final R after convergence: %v", finalR)

	if finalR <= initialR {
		t.Errorf("System failed to synchronize: Final R (%v) <= Initial R (%v)", finalR, initialR)
	}
}
