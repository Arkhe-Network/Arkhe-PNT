package adaptive

import (
	"math"
	"time"
)

// Mock graph and clustering packages for compilation
type UndirectedWeightedGraph struct {
	vertices map[string]time.Time
	edges    map[[2]string]float64
}

func NewUndirectedWeightedGraph() *UndirectedWeightedGraph {
	return &UndirectedWeightedGraph{
		vertices: make(map[string]time.Time),
		edges:    make(map[[2]string]float64),
	}
}

func (g *UndirectedWeightedGraph) AddVertex(id string, ts time.Time) {
	g.vertices[id] = ts
}

type Vertex struct {
	ID        string
	Timestamp time.Time
}

func (g *UndirectedWeightedGraph) Vertices() []Vertex {
	var vs []Vertex
	for id, ts := range g.vertices {
		vs = append(vs, Vertex{ID: id, Timestamp: ts})
	}
	return vs
}

func (g *UndirectedWeightedGraph) AddEdge(id1, id2 string, weight float64) {
	key := [2]string{id1, id2}
	if id1 > id2 {
		key = [2]string{id2, id1}
	}
	g.edges[key] = weight
}

func (g *UndirectedWeightedGraph) Weight(id1, id2 string) float64 {
	key := [2]string{id1, id2}
	if id1 > id2 {
		key = [2]string{id2, id1}
	}
	return g.edges[key]
}

func (g *UndirectedWeightedGraph) UpdateWeight(id1, id2 string, weight float64) {
	g.AddEdge(id1, id2, weight)
}

func (g *UndirectedWeightedGraph) AffinityMatrix() [][]float64 {
	return [][]float64{}
}

func Spectral(affinity [][]float64, clusters int) [][]string {
	return [][]string{}
}

type Query struct {
	DeviceIDs []string
}

func deviceIDInt(id string) int {
	return len(id) // Mock implementation
}

type Packager struct {
	graph       *UndirectedWeightedGraph
	theta       float64       // influence factor (0-1)
	queryWindow time.Duration // lookback for historical queries
}

func NewPackager(theta float64, window time.Duration) *Packager {
	return &Packager{
		graph:       NewUndirectedWeightedGraph(),
		theta:       theta,
		queryWindow: window,
	}
}

// AddDataPoint adds a new data point to the graph.
func (p *Packager) AddDataPoint(deviceID string, timestamp time.Time) {
	p.graph.AddVertex(deviceID, timestamp)
	// Initialize edges with Euclidean distance in (ID, time) space
	for _, other := range p.graph.Vertices() {
		if other.ID != deviceID {
			dist := math.Sqrt(math.Pow(float64(deviceIDInt(deviceID)-deviceIDInt(other.ID)), 2) +
				math.Pow(float64(timestamp.Unix()-other.Timestamp.Unix()), 2))
			p.graph.AddEdge(deviceID, other.ID, dist)
		}
	}
}

// UpdateWeights updates edge weights based on historical queries.
func (p *Packager) UpdateWeights(queries []Query) {
	// Count co‑occurrences of device pairs in queries
	cooccur := make(map[[2]string]int)
	for _, q := range queries {
		for i, a := range q.DeviceIDs {
			for _, b := range q.DeviceIDs[i+1:] {
				key := [2]string{a, b}
				if a > b {
					key = [2]string{b, a}
				}
				cooccur[key]++
			}
		}
	}
	for pair, count := range cooccur {
		oldWeight := p.graph.Weight(pair[0], pair[1])
		newWeight := p.theta*oldWeight + (1-p.theta)*float64(count)
		p.graph.UpdateWeight(pair[0], pair[1], newWeight)
	}
}

// Cluster returns the optimal batch groups using spectral clustering.
func (p *Packager) Cluster() [][]string {
	// Build affinity matrix from graph
	affinity := p.graph.AffinityMatrix()
	// Run spectral clustering
	clusters := Spectral(affinity, 0) // auto‑detect clusters
	// Convert back to device groups
	return clusters
}
