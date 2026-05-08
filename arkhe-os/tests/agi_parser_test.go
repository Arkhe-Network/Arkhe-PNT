package tests

import (
	"encoding/json"
	"testing"

	"arkhe/parser/frontends/agi"
	"arkhe/parser/frontends/agi/models"
)

func TestAGIParser(t *testing.T) {
	spec := models.Spec{
		Name:             "TestAGI",
		ArchitectureType: "NeuroSymbolic",
		Values: []models.Value{
			{
				ID:       "v1",
				Name:     "Safety First",
				Category: "ethical",
				Priority: "fundamental",
			},
		},
		Goals: []models.Goal{
			{
				ID:       "g1",
				Name:     "Ensure Wellbeing",
				Priority: "critical",
			},
		},
		Modules: []models.Module{
			{
				ID:   "m1",
				Name: "Perception",
				Type: "neural",
			},
		},
		SafetyMechanisms: []models.SafetyMechanism{
			{
				ID:            "s1",
				Name:          "Interrupt",
				MechanismType: "interruptibility",
				VerifiableProperties: []models.VerifiableProperty{
					{
						VerificationMethod: "formal_verification",
					},
				},
			},
		},
	}

	data, err := json.Marshal(spec)
	if err != nil {
		t.Fatalf("Failed to marshal spec: %v", err)
	}

	parser := agi.NewAGIParser()
	graph, err := parser.Parse(data, "test_spec.json", nil)
	if err != nil {
		t.Fatalf("Failed to parse AGI spec: %v", err)
	}

	if graph.Metrics.NodeCount != 5 {
		t.Errorf("Expected 5 nodes, got %d", graph.Metrics.NodeCount)
	}

	rootID := graph.RootNodes[0]
	rootNode, ok := graph.Nodes[rootID]
	if !ok {
		t.Fatalf("Root node missing")
	}

	if rootNode.Attributes["system_name"] != "TestAGI" {
		t.Errorf("Expected system_name to be TestAGI, got %v", rootNode.Attributes["system_name"])
	}

	if val, ok := rootNode.Attributes["coherence_alignment"].(float64); !ok || val <= 0 {
		t.Errorf("Expected coherence_alignment to be calculated, got %v", val)
	}

	if val, ok := rootNode.Attributes["coherence_safety"].(float64); !ok || val <= 0 {
		t.Errorf("Expected coherence_safety to be calculated, got %v", val)
	}
}
