package studio

import (
	"math"
	"math/cmplx"
	"sync"
)

// KuramotoScheduler manages the synchronization of Cooper nodes
type KuramotoScheduler struct {
	mu sync.RWMutex

	nodes []*CooperNode
	K     float64 // Dynamic coupling constant
	R     float64 // Order parameter (Global Coherence)
}

func NewKuramotoScheduler(nodes []*CooperNode) *KuramotoScheduler {
	return &KuramotoScheduler{
		nodes: nodes,
		K:     2.0,
	}
}

// CalculateOrderParameter computes the global coherence R and mean phase Psi
func (s *KuramotoScheduler) CalculateOrderParameter() (float64, float64) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	var sum complex128
	for _, node := range s.nodes {
		node.mu.RLock()
		sum += node.Phase
		node.mu.RUnlock()
	}

	N := float64(len(s.nodes))
	meanField := sum / complex(N, 0)
	s.R = cmplx.Abs(meanField)
	psi := cmplx.Phase(meanField)
	return s.R, psi
}

// UpdateCoupling adjusts K based on coherence R
func (s *KuramotoScheduler) UpdateCoupling() {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Dynamic coupling logic: K increases as R decreases (feedback to restore coherence)
	baseK := 2.0
	s.K = baseK * (1.0 + (1.0 - s.R))
}

// Step performs one integration step of the Kuramoto equations
func (s *KuramotoScheduler) Step(dt float64) {
	R, psi := s.CalculateOrderParameter()
	s.UpdateCoupling()

	s.mu.RLock()
	K := s.K
	s.mu.RUnlock()

	// Update each node's phase: d_theta_i = omega_i + K/N * sum(sin(theta_j - theta_i))
	// Mean-field version: d_theta_i = omega_i + K * R * sin(psi - theta_i)
	for _, node := range s.nodes {
		node.mu.Lock()

		currentAngle := cmplx.Phase(node.Phase)
		dTheta := node.Omega + K*R*math.Sin(psi-currentAngle)

		newAngle := currentAngle + dTheta*dt
		node.Phase = cmplx.Exp(complex(0, newAngle))

		node.mu.Unlock()
	}
}
