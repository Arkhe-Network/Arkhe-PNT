package selection

import (
	"context"
	"sort"
	"sync"
)

// Mock consensus package for compilation
type Engine struct{}

func (e *Engine) Commit(ctx context.Context, topic string, data interface{}) error {
	return nil
}

type NodeInfo struct {
	ID         string
	Distance   float64 // km (or latency)
	Storage    uint64  // remaining bytes
	Reputation float64 // from on‑chain records
	score      float64 // internal score
}

type Selector struct {
	consensus          *Engine
	nodes              map[string]*NodeInfo
	mu                 sync.RWMutex
	alpha, beta, gamma float64 // weighting for distance, storage, reputation
}

func NewSelector(engine *Engine, alpha, beta, gamma float64) *Selector {
	return &Selector{
		consensus: engine,
		nodes:     make(map[string]*NodeInfo),
		alpha:     alpha, beta: beta, gamma: gamma,
	}
}

func (s *Selector) RegisterNode(id string, dist float64, storage uint64, rep float64) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.nodes[id] = &NodeInfo{ID: id, Distance: dist, Storage: storage, Reputation: rep}
}

// Score calculates the evaluation score for a node.
func (s *Selector) Score(node *NodeInfo) float64 {
	return s.alpha*node.Distance + s.beta*float64(node.Storage) + s.gamma*node.Reputation
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Select returns the optimal node(s) using consensus.
func (s *Selector) Select(ctx context.Context, k int) ([]*NodeInfo, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// Compute scores
	scored := make([]*NodeInfo, 0, len(s.nodes))
	for _, n := range s.nodes {
		n.score = s.Score(n)
		scored = append(scored, n)
	}
	// Sort by score
	sort.Slice(scored, func(i, j int) bool { return scored[i].score < scored[j].score })

	// Select top k nodes
	selected := scored[:min(k, len(scored))]

	// Now commit the selection via consensus (a round of PBFT-like voting)
	// The consensus engine already handles phase synchronization; we reuse it.
	// The selection is broadcast to all nodes, and they confirm using the consensus protocol.
	err := s.consensus.Commit(ctx, "storage_selection", selected)
	if err != nil {
		return nil, err
	}
	return selected, nil
}
