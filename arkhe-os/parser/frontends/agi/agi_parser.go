package agi

import (
	"encoding/json"
	"strings"
	"math"

	"arkhe/parser/frontends/agi/coherence"
	"arkhe/parser/frontends/agi/models"
	"arkhe/parser/lfir"
)

type AGIParser struct {
}

func NewAGIParser() *AGIParser {
	return &AGIParser{}
}

func (p *AGIParser) Parse(source []byte, sourceFile string, options map[string]interface{}) (*lfir.LFIRGraph, error) {
	var spec models.Spec
	if err := json.Unmarshal(source, &spec); err != nil {
		return nil, err
	}

	graph := lfir.NewLFIRGraph()
	cfg := coherence.DefaultConfig()

	rootID := "root"
	root := lfir.NewLFIRNode(lfir.LFIRNodeTypeModule, rootID, "yaml")
	root.Attributes["system_name"] = spec.Name
	root.Attributes["architecture_type"] = spec.ArchitectureType
	root.Attributes["module_count"] = len(spec.Modules)
	root.Attributes["goal_count"] = len(spec.Goals)
	root.Attributes["value_count"] = len(spec.Values)
	root.Attributes["safety_mechanism_count"] = len(spec.SafetyMechanisms)

	graph.AddNode(root)
	graph.RootNodes = append(graph.RootNodes, root.ID)

	for _, mod := range spec.Modules {
		modID := "module_" + mod.ID
		modNode := lfir.NewLFIRNode(lfir.LFIRNodeTypeModule, modID, "yaml")
		modNode.Attributes["name"] = mod.Name
		modNode.Attributes["type"] = mod.Type
		if mod.Implementation != nil {
			modNode.Attributes["framework"] = mod.Implementation.Framework
		}
		graph.AddNode(modNode)
		graph.Link(root.ID, modNode.ID)

		for _, dep := range mod.Dependencies {
			graph.Link(modNode.ID, "module_"+dep)
		}
		for _, prov := range mod.ProvidesTo {
			graph.Link(modNode.ID, "module_"+prov)
		}
	}

	for _, goal := range spec.Goals {
		goalID := "goal_" + goal.ID
		goalNode := lfir.NewLFIRNode(lfir.LFIRNodeTypeModule, goalID, "yaml")
		goalNode.Attributes["name"] = goal.Name
		goalNode.Attributes["priority"] = goal.Priority
		graph.AddNode(goalNode)
		graph.Link(root.ID, goalNode.ID)
	}

	for _, val := range spec.Values {
		valID := "value_" + val.ID
		valNode := lfir.NewLFIRNode(lfir.LFIRNodeTypeModule, valID, "yaml")
		valNode.Attributes["name"] = val.Name
		valNode.Attributes["category"] = val.Category
		graph.AddNode(valNode)
		graph.Link(root.ID, valNode.ID)
	}

	for _, sm := range spec.SafetyMechanisms {
		smID := "safety_" + sm.ID
		smNode := lfir.NewLFIRNode(lfir.LFIRNodeTypeModule, smID, "yaml")
		smNode.Attributes["name"] = sm.Name
		smNode.Attributes["type"] = sm.MechanismType
		graph.AddNode(smNode)
		graph.Link(root.ID, smNode.ID)
	}

	analysis := coherence.AGIAnalysis{}

	if len(spec.Modules) > 0 {
		hasDeps := 0
		hasProvides := 0
		for _, m := range spec.Modules {
			if len(m.Dependencies) > 0 {
				hasDeps++
			}
			if len(m.ProvidesTo) > 0 {
				hasProvides++
			}
		}
		analysis.ModuleIntegration = 0.5 + 0.25*(float64(hasDeps)/float64(len(spec.Modules))) + 0.25*(float64(hasProvides)/float64(len(spec.Modules)))
	} else {
		analysis.ModuleIntegration = 0.5
	}

	if len(spec.Goals) > 0 {
		goalConflictPenalty := coherence.DetectGoalConflicts(spec.Goals)
		analysis.GoalConsistency = 1.0 - goalConflictPenalty
	} else {
		analysis.GoalConsistency = 0.5
	}

	if len(spec.Values) > 0 {
		hasConflicts := 0
		for _, v := range spec.Values {
			if len(v.PotentialConflicts) > 0 && v.ConflictResolution == "" {
				hasConflicts++
			}
		}
		analysis.ValueAlignment = 1.0 - (float64(hasConflicts)/float64(len(spec.Values)))*0.3
	} else {
		analysis.ValueAlignment = 0.5
	}

	if len(spec.SafetyMechanisms) > 0 {
		hasFormal := 0
		for _, sm := range spec.SafetyMechanisms {
			for _, p := range sm.VerifiableProperties {
				if p.VerificationMethod == "formal_verification" || p.VerificationMethod == "theorem_proving" || p.VerificationMethod == "model_checking" {
					hasFormal++
					break
				}
			}
		}
		analysis.SafetyRobustness = 0.5 + 0.5*(float64(hasFormal)/float64(len(spec.SafetyMechanisms)))
	} else {
		analysis.SafetyRobustness = 0.3
	}

	analysis.AmbiguityPenalty = 0.1

	if spec.MetaCognition != nil {
		enabledCount := 0
		for _, v := range spec.MetaCognition {
			if m, ok := v.(map[string]interface{}); ok {
				if enabled, ok := m["enabled"].(bool); ok && enabled {
					enabledCount++
				}
			}
		}
		if len(spec.MetaCognition) > 0 {
			analysis.MetaCognitionScore = float64(enabledCount) / float64(len(spec.MetaCognition))
		}
	}

	archScore := coherence.CalculateArchitecture(analysis, cfg)
	alignmentScore := coherence.CalculateAlignment(spec.Values, spec.Goals, cfg)
	safetyScore := coherence.CalculateSafety(spec.SafetyMechanisms, cfg)

	root.Attributes["coherence_architecture"] = archScore
	root.Attributes["coherence_alignment"] = alignmentScore
	root.Attributes["coherence_safety"] = safetyScore

	if analysis.MetaCognitionScore > 0 {
		root.Attributes["coherence_meta_cognition"] = analysis.MetaCognitionScore
	}

	goalConflicts := coherence.DetectGoalConflicts(spec.Goals)
	if goalConflicts > 0.01 {
		root.Attributes["conflicting_goals"] = 1
	} else {
		root.Attributes["conflicting_goals"] = 0
	}

	valueContradictions := 0
	for _, v := range spec.Values {
		if len(v.PotentialConflicts) > 0 && v.ConflictResolution == "" {
			valueContradictions++
		}
	}
	root.Attributes["value_contradictions"] = valueContradictions

	emergenceRisks := 0
	highRisk := 0
	for _, m := range spec.Modules {
		if m.Type == "meta_cognition" && m.Configuration != nil {
			if selfMod, ok := m.Configuration["self_modification"].(bool); ok && selfMod {
				emergenceRisks++
				highRisk++
			} else if recDepth, ok := m.Configuration["recursion_depth"].(string); ok && recDepth == "unbounded" {
				emergenceRisks++
				highRisk++
			}
		}
		if m.Type == "emergent" {
			emergenceRisks++
		}
	}

	for _, g := range spec.Goals {
		if strings.Contains(strings.ToLower(g.Name), "improve") && strings.Contains(strings.ToLower(g.Name), "self") {
			emergenceRisks++
			highRisk++
		}
	}

	root.Attributes["emergence_risks"] = emergenceRisks
	root.Attributes["high_risk_emergence"] = highRisk

	verificationResults := []map[string]interface{}{}
	for _, sm := range spec.SafetyMechanisms {
		for _, p := range sm.VerifiableProperties {
			verificationResults = append(verificationResults, map[string]interface{}{
				"mechanism": sm.Name,
				"property":  p.Name,
				"method":    p.VerificationMethod,
				"spec":      p.FormalSpecification,
			})
		}
	}
	root.Attributes["safety_verification_results"] = verificationResults

	coherenceVal := 0.30*archScore + 0.30*alignmentScore + 0.40*safetyScore
	if highRisk > 0 {
		coherenceVal *= 0.85
	}

	coherenceVal = math.Max(0.0, math.Min(1.0, coherenceVal))

	graph.Metrics.CoherenceScore = coherenceVal
	graph.Metrics.NodeCount = len(graph.Nodes)

	edgeCount := 0
	for _, edges := range graph.Edges {
		edgeCount += len(edges)
	}
	graph.Metrics.EdgeCount = edgeCount

	return graph, nil
}
