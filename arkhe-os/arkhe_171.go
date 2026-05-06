package main

import (
	"fmt"
	"math"
	"sync"
)

// ============================================================
// SUBSTRATO 171: Protocolo de Roteamento por Coerência Distribuída
// ============================================================

// RoutingTableEntry holds route information prioritizing coherence and resonance
type RoutingTableEntry struct {
	Destination  CosmicAddress
	PrefixLen    int
	NextHop      string  // NodeID of the next hop
	Coherence    float64 // $\Phi_C$ value for this route
	Entanglement float64 // Measure of entanglement (lower entropy = higher entanglement)
	Cost         float64 // Computed path cost (e.g. von Neumann entropy)
}

// CoherenceRouter manages the routing tables and field interactions
type CoherenceRouter struct {
	mu           sync.RWMutex
	LocalNodeID  string
	LocalAddress CosmicAddress
	Routes       map[string]*RoutingTableEntry // key is dest/prefix
	Neighbors    map[string]*CosmicNode
	Engine       *CosmologyEngine
}

func NewCoherenceRouter(engine *CosmologyEngine, localNodeID string, localAddr CosmicAddress) *CoherenceRouter {
	return &CoherenceRouter{
		LocalNodeID:  localNodeID,
		LocalAddress: localAddr,
		Routes:       make(map[string]*RoutingTableEntry),
		Neighbors:    make(map[string]*CosmicNode),
		Engine:       engine,
	}
}

// AddNeighbor adds a direct quantum link to another node
func (cr *CoherenceRouter) AddNeighbor(node *CosmicNode) {
	cr.mu.Lock()
	defer cr.mu.Unlock()
	cr.Neighbors[node.ID] = node
}

// UpdateRoute adds or updates a route if it has higher coherence/lower entropy
func (cr *CoherenceRouter) UpdateRoute(dest CosmicAddress, prefixLen int, nextHop string, coherence, entanglement, cost float64) {
	cr.mu.Lock()
	defer cr.mu.Unlock()

	key := fmt.Sprintf("%x/%d", dest[:prefixLen/8], prefixLen)

	existing, exists := cr.Routes[key]
	if !exists || coherence > existing.Coherence || (coherence == existing.Coherence && cost < existing.Cost) {
		cr.Routes[key] = &RoutingTableEntry{
			Destination:  dest,
			PrefixLen:    prefixLen,
			NextHop:      nextHop,
			Coherence:    coherence,
			Entanglement: entanglement,
			Cost:         cost,
		}
	}
}

// CalculatePhiInteraction computes the resonance field $\Phi_C \cdot \Phi_C'$ between two nodes
func (cr *CoherenceRouter) CalculatePhiInteraction(nodeA, nodeB *CosmicNode) float64 {
	// A simple interaction model based on coherence and resonance
	return nodeA.Coherence * nodeB.Coherence * math.Exp(-math.Abs(nodeA.Resonance-nodeB.Resonance))
}

// FindBestRoute uses the $\Phi_C$ field geometry to find the next hop
func (cr *CoherenceRouter) FindBestRoute(destAddr CosmicAddress) (*RoutingTableEntry, error) {
	cr.mu.RLock()
	defer cr.mu.RUnlock()

	var bestRoute *RoutingTableEntry
	var bestMatchLen int = -1

	// Longest prefix match with coherence priority
	for _, route := range cr.Routes {
		if destAddr.IsInSubnet(route.Destination, route.PrefixLen) {
			if route.PrefixLen > bestMatchLen {
				bestMatchLen = route.PrefixLen
				bestRoute = route
			} else if route.PrefixLen == bestMatchLen {
				// Tie-breaker based on coherence
				if route.Coherence > bestRoute.Coherence {
					bestRoute = route
				}
			}
		}
	}

	if bestRoute != nil {
		return bestRoute, nil
	}
	return nil, fmt.Errorf("no route found for %s", destAddr.String())
}

// PropagateField propagates routing information to neighbors, simulating the emergence of network geometry
func (cr *CoherenceRouter) PropagateField() {
	cr.mu.RLock()
	neighbors := cr.Neighbors
	cr.mu.RUnlock()

	for _, neighbor := range neighbors {
		// Calculate the interaction field with this neighbor
		localNode := cr.Engine.Nodes[cr.LocalNodeID]
		if localNode == nil {
			continue
		}

		phiInteraction := cr.CalculatePhiInteraction(localNode, neighbor)

		// In a real implementation, we would send our routing table to the neighbor,
		// adjusting the cost based on the phiInteraction (higher interaction = lower cost)
		// For simulation, we log it
		// fmt.Printf("Propagating field from %s to %s with interaction strength %.4f\n", cr.LocalNodeID, neighbor.ID, phiInteraction)
		_ = phiInteraction
	}
}

// RoutePacket intercepts packet routing to use the Coherence Field
func (cr *CoherenceRouter) RoutePacket(packet []byte, destAddr CosmicAddress) error {
	route, err := cr.FindBestRoute(destAddr)
	if err != nil {
		return fmt.Errorf("coherence routing failed: %v", err)
	}

	fmt.Printf("Coherence Field Routing: Packet to %s via Next Hop %s (Coherence: %.3f)\n", destAddr.String(), route.NextHop, route.Coherence)
	return nil
}

func InitSubstrate171() {
	fmt.Println("\n[SUBSTRATO 171] Protocolo de Roteamento por Coerência Distribuída")
	engine := NewCosmologyEngine()

	engine.RegisterNode("NODE_A", "Alpha", ScalePlanetary, 0.95, 0.8)
	engine.RegisterNode("NODE_B", "Beta", ScalePlanetary, 0.90, 0.75)
	engine.RegisterNode("GATEWAY", "Gateway", ScaleStellar, 0.99, 0.9)

	nodeAAddr := NewCosmicAddress(ScalePlanetary, 0.95, 0.8, 0.0, 0.0, 0, "Alpha")
	nodeBAddr := NewCosmicAddress(ScalePlanetary, 0.90, 0.75, 0.0, 0.0, 0, "Beta")
	gatewayAddr := NewCosmicAddress(ScaleStellar, 0.99, 0.9, 0.0, 0.0, 0, "Gateway")

	routerA := NewCoherenceRouter(engine, "NODE_A", nodeAAddr)
	routerA.AddNeighbor(engine.Nodes["GATEWAY"])

	// Simulating routing table population from the field
	// Node A learns route to Node B via Gateway
	routerA.UpdateRoute(nodeBAddr.Network(16), 16, "GATEWAY", 0.92, 0.1, 0.5)

	// Direct route (hypothetical quantum tunnel)
	routerA.UpdateRoute(nodeBAddr, 256, "NODE_B", 0.98, 0.01, 0.1)

	packet := []byte("quantum_echo")
	fmt.Printf("Sending packet from A to B (%s)\n", nodeBAddr.String())
	err := routerA.RoutePacket(packet, nodeBAddr)
	if err != nil {
		fmt.Println(err)
	}

	fmt.Printf("Sending packet from A to unknown gateway (%s)\n", gatewayAddr.String())
	err = routerA.RoutePacket(packet, gatewayAddr)
	if err != nil {
		fmt.Println("Expected error:", err)
	}
}
