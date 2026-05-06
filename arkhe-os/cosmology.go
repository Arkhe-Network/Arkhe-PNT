package main

import ()

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

func (cs CosmicScale) String() string {
	names := []string{
		"Quantum Foam", "Particle Cloud", "Atomic Network",
		"Cellular Mesh", "Organism Net", "Ecosystem Grid",
		"Planetary Net", "Stellar Link", "Galactic Web",
		"Cluster Fabric", "Supercluster Backbone", "Horizon Edge",
		"Multiverse Root",
	}
	if int(cs) < len(names) {
		return names[cs]
	}
	return "UNKNOWN"
}

type CosmicNode struct {
	ID        string
	Name      string
	Scale     CosmicScale
	Coherence float64
	Resonance float64
}

type CosmologyEngine struct {
	Nodes map[string]*CosmicNode
}

func NewCosmologyEngine() *CosmologyEngine {
	return &CosmologyEngine{
		Nodes: make(map[string]*CosmicNode),
	}
}

func (ce *CosmologyEngine) RegisterNode(id string, name string, scale CosmicScale, coherence float64, resonance float64) {
	ce.Nodes[id] = &CosmicNode{
		ID:        id,
		Name:      name,
		Scale:     scale,
		Coherence: coherence,
		Resonance: resonance,
	}
}
