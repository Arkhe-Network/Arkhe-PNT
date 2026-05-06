package evolution

import (
	"fmt"
	"math"
	"sync"
	"time"
)

// KernelMetaLearningParameters hold adaptive parameters improved via meta-reflection
type KernelMetaLearningParameters struct {
	MinSamplesForInsight  int           `json:"min_samples_for_insight"`
	ReflectionWindow      time.Duration `json:"reflection_window"`
	RiskAversionFactor    float64       `json:"risk_aversion_factor"`
	ConsensusThreshold    float64       `json:"consensus_threshold"`
	CriticalThreshold     float64       `json:"critical_threshold"`
	InsightValueThreshold float64       `json:"insight_value_threshold"` // Minimum Value * Confidence
}

// ProposalOutcome stores the result of an applied optimization proposal
type ProposalOutcome struct {
	ProposalID   string
	KernelID     string
	Type         KernelOptimizationType
	ExpectedGain float64
	ObservedGain float64
	Success      bool
	Timestamp    time.Time
}

// KernelMetaReflector learns to reflect better by analyzing past proposal outcomes
type KernelMetaReflector struct {
	mu sync.RWMutex

	kernelID   string
	parameters KernelMetaLearningParameters
	outcomes   []ProposalOutcome
}

func NewKernelMetaReflector(kernelID string) *KernelMetaReflector {
	return &KernelMetaReflector{
		kernelID: kernelID,
		parameters: KernelMetaLearningParameters{
			MinSamplesForInsight:  20,
			ReflectionWindow:      60 * time.Minute,
			RiskAversionFactor:    0.4,
			ConsensusThreshold:    0.67,
			CriticalThreshold:     0.80,
			InsightValueThreshold: 0.15,
		},
		outcomes: make([]ProposalOutcome, 0),
	}
}

// RecordOutcome records the real-world outcome of an applied proposal
func (m *KernelMetaReflector) RecordOutcome(outcome ProposalOutcome) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.outcomes = append(m.outcomes, outcome)

	// Keep a bounded history
	if len(m.outcomes) > 1000 {
		m.outcomes = m.outcomes[100:]
	}
}

// PerformMetaReflection evaluates outcomes and updates parameters to reflect better
func (m *KernelMetaReflector) PerformMetaReflection() (*KernelMetaLearningParameters, error) {
	m.mu.Lock()
	defer m.mu.Unlock()

	if len(m.outcomes) < 5 {
		return &m.parameters, fmt.Errorf("insufficient outcomes for meta-reflection")
	}

	// Calculate accuracy of expected vs observed gain
	var totalDiff, successRate float64
	successCount := 0

	for _, o := range m.outcomes {
		totalDiff += math.Abs(o.ExpectedGain - o.ObservedGain)
		if o.Success {
			successCount++
		}
	}
	avgDiff := totalDiff / float64(len(m.outcomes))
	successRate = float64(successCount) / float64(len(m.outcomes))

	// Adjust Risk Aversion
	if successRate < 0.70 {
		m.parameters.RiskAversionFactor = math.Min(0.9, m.parameters.RiskAversionFactor+0.1)
		m.parameters.ConsensusThreshold = math.Min(0.9, m.parameters.ConsensusThreshold+0.05)
	} else if successRate > 0.90 && avgDiff < 0.01 {
		m.parameters.RiskAversionFactor = math.Max(0.1, m.parameters.RiskAversionFactor-0.05)
	}

	// Adjust Reflection Window based on predictability (avgDiff)
	if avgDiff > 0.05 {
		// Kernel behavior is volatile, shorten window for faster reaction
		newWindow := time.Duration(float64(m.parameters.ReflectionWindow) * 0.8)
		if newWindow >= 10*time.Minute {
			m.parameters.ReflectionWindow = newWindow
		}
	} else {
		// Kernel is stable, lengthen window for broader patterns
		newWindow := time.Duration(float64(m.parameters.ReflectionWindow) * 1.1)
		if newWindow <= 24*time.Hour {
			m.parameters.ReflectionWindow = newWindow
		}
	}

	// Adjust minimum insight value threshold based on noise
	if successRate < 0.60 {
		m.parameters.InsightValueThreshold = math.Min(0.5, m.parameters.InsightValueThreshold+0.05)
	} else {
		m.parameters.InsightValueThreshold = math.Max(0.05, m.parameters.InsightValueThreshold-0.02)
	}

	return &m.parameters, nil
}

// GetParameters returns the current meta-learned parameters
func (m *KernelMetaReflector) GetParameters() KernelMetaLearningParameters {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.parameters
}
