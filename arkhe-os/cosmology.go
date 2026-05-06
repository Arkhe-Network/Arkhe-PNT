package main

import (
	"fmt"
	"math"
	"sync"
)

type CosmicScale int

const (
	ScaleQuantum CosmicScale = iota
	ScaleParticle
	ScaleAtomic
	ScaleCellular
	ScaleOrganism
	ScaleEcosystem
	ScalePlanetary
	ScaleStellar
	ScaleGalactic
	ScaleCluster
	ScaleSupercluster
	ScaleHorizon
	ScaleMultiverse
)

type CosmicNode struct {
	ID        string
	Name      string
	Scale     CosmicScale
	Coherence float64
	Resonance float64
}

type TeleportationChannel struct {
	ChannelID            string
	SourceNode           string
	TargetNode           string
	EntanglementFidelity float64
	ChannelState         string
}

type CosmologyEngine struct {
	mu       sync.RWMutex
	Nodes    map[string]*CosmicNode
	Channels map[string]*TeleportationChannel
}

func NewCosmologyEngine() *CosmologyEngine {
	return &CosmologyEngine{
		Nodes:    make(map[string]*CosmicNode),
		Channels: make(map[string]*TeleportationChannel),
	}
}

func (ce *CosmologyEngine) RegisterNode(id string, name string, scale CosmicScale, coherence float64, resonance float64) {
	ce.mu.Lock()
	defer ce.mu.Unlock()
	ce.Nodes[id] = &CosmicNode{
		ID:        id,
		Name:      name,
		Scale:     scale,
		Coherence: coherence,
		Resonance: resonance,
	}
}

func (s CosmicScale) String() string {
	names := []string{
		"Quantum", "Particle", "Atomic", "Cellular", "Organism",
		"Ecosystem", "Planetary", "Stellar", "Galactic", "Cluster",
		"Supercluster", "Horizon", "Multiverse",
	}
	if int(s) < len(names) {
		return names[s]
	}
	return "Unknown"
}

func (ce *CosmologyEngine) EstablishTeleportationChannel(sourceID, targetID string) (*TeleportationChannel, error) {
	ce.mu.Lock()
	defer ce.mu.Unlock()

	chID := fmt.Sprintf("CH_%s_%s", sourceID, targetID)
	ch := &TeleportationChannel{
		ChannelID:            chID,
		SourceNode:           sourceID,
		TargetNode:           targetID,
		EntanglementFidelity: 0.99,
		ChannelState:         "ACTIVE",
	}
	ce.Channels[chID] = ch
	return ch, nil
}

func (ce *CosmologyEngine) SimulateResonance(id string) float64 {
	ce.mu.RLock()
	defer ce.mu.RUnlock()
	if node, ok := ce.Nodes[id]; ok {
		return node.Resonance * math.E
	}
	return 0.0
}
