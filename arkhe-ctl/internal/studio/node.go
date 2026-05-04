package studio

import (
	"encoding/json"
	"fmt"
	"math/cmplx"
	"sync"
	"time"

	"github.com/nats-io/nats.go"
)

// CooperNode represents a node in the cluster
type CooperNode struct {
	ID    int
	Phase complex128 // θ(t) represented as a complex phase
	Omega float64    // Natural frequency ω

	nc   *nats.Conn
	sub  *nats.Subscription
	mu   sync.RWMutex
}

// PhaseMessage is the payload for NATS pub/sub
type PhaseMessage struct {
	SenderID int     `json:"sender_id"`
	Real     float64 `json:"real"`
	Imag     float64 `json:"imag"`
	Timestamp int64   `json:"timestamp"`
}

func NewCooperNode(id int, omega float64, natsURL string) (*CooperNode, error) {
	nc, err := nats.Connect(natsURL)
	if err != nil {
		return nil, err
	}

	return &CooperNode{
		ID:    id,
		Phase: cmplx.Exp(complex(0, 0)),
		Omega: omega,
		nc:    nc,
	}, nil
}

func (n *CooperNode) Start(ctx_done <-chan struct{}) {
	if n.nc == nil {
		fmt.Printf("🜏 [NODE %d] Running in isolated mode (No NATS)\n", n.ID)
		<-ctx_done
		return
	}

	// Subscribe to phase updates
	sub, err := n.nc.Subscribe("arkhe.phase.sync", func(m *nats.Msg) {
		var msg PhaseMessage
		if err := json.Unmarshal(m.Data, &msg); err != nil {
			return
		}
		if msg.SenderID == n.ID {
			return
		}

		n.applyCoupling(msg)
	})
	if err != nil {
		fmt.Printf("Node %d failed to subscribe: %v\n", n.ID, err)
		return
	}
	n.sub = sub

	// Broadcast loop
	ticker := time.NewTicker(50 * time.Millisecond) // Increased frequency
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			n.broadcastPhase()
		case <-ctx_done:
			n.nc.Close()
			return
		}
	}
}

func (n *CooperNode) applyCoupling(msg PhaseMessage) {
	n.mu.Lock()
	defer n.mu.Unlock()

	// Distributed phase coupling: each node slightly pulls towards incoming phases
	// This complements the global scheduler
	incomingPhase := complex(msg.Real, msg.Imag)
	couplingStrength := 0.05
	n.Phase = n.Phase + complex(couplingStrength, 0)*(incomingPhase - n.Phase)
	n.Phase /= complex(cmplx.Abs(n.Phase), 0) // Normalize
}

func (n *CooperNode) broadcastPhase() {
	n.mu.RLock()
	p := n.Phase
	n.mu.RUnlock()

	msg := PhaseMessage{
		SenderID: n.ID,
		Real:     real(p),
		Imag:     imag(p),
		Timestamp: time.Now().UnixNano(),
	}
	data, _ := json.Marshal(msg)
	n.nc.Publish("arkhe.phase.sync", data)
}

// LogicalAgent represents one of the 49 agents in the studio
type LogicalAgent struct {
	ID int
}

func NewLogicalAgent(id int) *LogicalAgent {
	return &LogicalAgent{ID: id}
}

func (a *LogicalAgent) Start(ctx_done <-chan struct{}) {
	// Logical agents perform high-level tasks or monitoring
	ticker := time.NewTicker(500 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			// Agent task simulation
		case <-ctx_done:
			return
		}
	}
}
