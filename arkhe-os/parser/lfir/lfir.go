package lfir

import (
	"encoding/json"
	"os"
)

// LFIRNodeType is the type of a node in the Lingua Franca Intermediate Representation.
type LFIRNodeType string

const (
	LFIRNodeTypeModule    LFIRNodeType = "LFIRModule"
	LFIRNodeTypeOperation LFIRNodeType = "LFIROperation"
	LFIRNodeTypeType      LFIRNodeType = "LFIRType"
	LFIRNodeTypeMetadata  LFIRNodeType = "LFIRMetadata"
	LFIRNodeTypeCall      LFIRNodeType = "LFIRCall"
	LFIRNodeTypeExpr      LFIRNodeType = "LFIRExpr"
)

type LFIRNode struct {
	ID         string
	Type       LFIRNodeType
	Name       string
	SourceLang string
	Namespace  string
	Attributes map[string]interface{}
}

func NewLFIRNode(nodeType LFIRNodeType, name string, sourceLang string) *LFIRNode {
	return &LFIRNode{
		ID:         name + "_" + string(nodeType),
		Type:       nodeType,
		Name:       name,
		SourceLang: sourceLang,
		Attributes: make(map[string]interface{}),
	}
}

type LFIRMetrics struct {
	CoherenceScore float64
	NodeCount      int
	EdgeCount      int
}

type LFIRGraph struct {
	RootNodes []string
	Nodes     map[string]*LFIRNode
	Edges     map[string][]string // directed edges parent -> children
	Metrics   LFIRMetrics
}

func NewLFIRGraph() *LFIRGraph {
	return &LFIRGraph{
		RootNodes: make([]string, 0),
		Nodes:     make(map[string]*LFIRNode),
		Edges:     make(map[string][]string),
	}
}

func (g *LFIRGraph) AddNode(node *LFIRNode) {
	g.Nodes[node.ID] = node
}

func (g *LFIRGraph) Link(parentID, childID string) {
	g.Edges[parentID] = append(g.Edges[parentID], childID)
}

func (g *LFIRGraph) ToJSONFile(path string) error {
	b, err := json.MarshalIndent(g, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, b, 0644)
}

func (g *LFIRGraph) FindNodeByAttribute(key string, val interface{}) (*LFIRNode, bool) {
	for _, n := range g.Nodes {
		if v, ok := n.Attributes[key]; ok && v == val {
			return n, true
		}
	}
	return nil, false
}
