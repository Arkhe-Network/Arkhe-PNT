package studio

import (
	"bytes"
	"encoding/json"
	"fmt"
	"math/cmplx"
	"net/http"
	"time"
)

// AkashaState reflects the global cluster state
type AkashaState struct {
	Timestamp int64     `json:"timestamp"`
	R         float64   `json:"coherence_r"`
	K         float64   `json:"coupling_k"`
	Nodes     []float64 `json:"node_phases"`
}

func (s *KuramotoScheduler) AnchorToAkasha(ledgerURL string, ctx_done <-chan struct{}) {
	ticker := time.NewTicker(200 * time.Millisecond) // Increased anchoring frequency
	defer ticker.Stop()

	client := &http.Client{Timeout: 100 * time.Millisecond}

	for {
		select {
		case <-ticker.C:
			s.mu.RLock()
			state := AkashaState{
				Timestamp: time.Now().UnixNano(),
				R:         s.R,
				K:         s.K,
				Nodes:     make([]float64, len(s.nodes)),
			}
			for i, node := range s.nodes {
				node.mu.RLock()
				state.Nodes[i] = cmplx.Phase(node.Phase)
				node.mu.RUnlock()
			}
			s.mu.RUnlock()

			data, _ := json.Marshal(state)

			// Reflecting the state in Akasha Ledger
			req, err := http.NewRequest("POST", ledgerURL, bytes.NewBuffer(data))
			if err != nil {
				continue
			}
			req.Header.Set("Content-Type", "application/json")

			// Attempt to anchor (failure is logged but non-blocking)
			resp, err := client.Do(req)
			if err != nil {
				// For simulation, we log the intent
				fmt.Printf("🜏 [AKASHA] Anchoring attempt: R=%.6f, K=%.4f\n", state.R, state.K)
			} else {
				resp.Body.Close()
			}

		case <-ctx_done:
			return
		}
	}
}
