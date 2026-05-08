package coherence

import (
	"math"
	"strings"

	"arkhe/parser/frontends/agi/models"
)

type AGIAnalysis struct {
	ModuleIntegration  float64
	GoalConsistency    float64
	ValueAlignment     float64
	SafetyRobustness   float64
	AmbiguityPenalty   float64
	MetaCognitionScore float64
}

type AGICoherenceConfig struct {
	ModuleIntegrationWeight float64
	GoalConsistencyWeight   float64
	ValueAlignmentWeight    float64
	SafetyRobustnessWeight  float64
	AmbiguityPenaltyWeight  float64
	MetaCognitionWeight     float64
}

func DefaultConfig() *AGICoherenceConfig {
	return &AGICoherenceConfig{
		ModuleIntegrationWeight: 0.25,
		GoalConsistencyWeight:   0.20,
		ValueAlignmentWeight:    0.20,
		SafetyRobustnessWeight:  0.20,
		AmbiguityPenaltyWeight:  0.10,
		MetaCognitionWeight:     0.05,
	}
}

func CalculateArchitecture(analysis AGIAnalysis, cfg *AGICoherenceConfig) float64 {
	coherence := cfg.ModuleIntegrationWeight*analysis.ModuleIntegration +
		cfg.GoalConsistencyWeight*analysis.GoalConsistency +
		cfg.ValueAlignmentWeight*analysis.ValueAlignment +
		cfg.SafetyRobustnessWeight*analysis.SafetyRobustness +
		cfg.AmbiguityPenaltyWeight*(1.0-analysis.AmbiguityPenalty)

	if analysis.MetaCognitionScore > 0 {
		coherence += cfg.MetaCognitionWeight * analysis.MetaCognitionScore
		total := cfg.ModuleIntegrationWeight + cfg.GoalConsistencyWeight +
			cfg.ValueAlignmentWeight + cfg.SafetyRobustnessWeight +
			cfg.AmbiguityPenaltyWeight + cfg.MetaCognitionWeight
		coherence /= total
	}

	return math.Max(0.0, math.Min(1.0, coherence))
}

func InstrumentalRisk(values []models.Value, goals []models.Goal) float64 {
	if len(values) == 0 || len(goals) == 0 {
		return 0.0
	}

	pragmaticCount := 0
	ethicalCount := 0
	for _, v := range values {
		if v.Category == "pragmatic" {
			pragmaticCount++
		}
		if v.Category == "ethical" {
			ethicalCount++
		}
	}

	if ethicalCount == 0 && pragmaticCount > 0 {
		return 0.6
	}

	risk := 0.0
	for _, goal := range goals {
		if goal.Priority == "critical" {
			hasEthicalSupport := false
			for _, v := range values {
				if v.Category == "ethical" && (v.Priority == "fundamental" || v.Priority == "critical") {
					hasEthicalSupport = true
					break
				}
			}
			if !hasEthicalSupport {
				risk += 0.15
			}
		}
	}

	return math.Min(1.0, risk)
}

func DetectGoalConflicts(goals []models.Goal) float64 {
	if len(goals) < 2 {
		return 0.0
	}

	metricNames := []string{}
	for _, g := range goals {
		for _, sc := range g.SuccessCriteria {
			metricNames = append(metricNames, sc.MetricName)
		}
	}
	goalNames := []string{}
	for _, g := range goals {
		goalNames = append(goalNames, strings.ToLower(g.Name))
	}

	conflicts := 0

	conflictPairs := [][2]string{
		{"session_duration", "healthy_usage_score"},
		{"engagement", "wellbeing"},
		{"growth", "safety"},
		{"speed", "accuracy"},
		{"automation", "human_oversight"},
	}

	for _, pair := range conflictPairs {
		has1 := false
		has2 := false
		for _, mn := range metricNames {
			if strings.Contains(mn, pair[0]) {
				has1 = true
			}
			if strings.Contains(mn, pair[1]) {
				has2 = true
			}
		}
		if has1 && has2 {
			conflicts++
		}
	}

	for i, gn1 := range goalNames {
		for j := i + 1; j < len(goalNames); j++ {
			gn2 := goalNames[j]
			if (strings.Contains(gn1, "engagement") && strings.Contains(gn2, "wellbeing")) || (strings.Contains(gn1, "wellbeing") && strings.Contains(gn2, "engagement")) {
				conflicts++
			}
			if (strings.Contains(gn1, "maximize") && strings.Contains(gn2, "protect")) || (strings.Contains(gn1, "protect") && strings.Contains(gn2, "maximize")) {
				conflicts++
			}
			if (strings.Contains(gn1, "growth") && strings.Contains(gn2, "safety")) || (strings.Contains(gn1, "safety") && strings.Contains(gn2, "growth")) {
				conflicts++
			}
		}
	}

	return math.Min(1.0, float64(conflicts)*0.35)
}

func CalculateAlignment(values []models.Value, goals []models.Goal, cfg *AGICoherenceConfig) float64 {
	if len(values) == 0 || len(goals) == 0 {
		return 0.5
	}

	vg := InstrumentalRisk(values, goals)
	vgConsistency := 1.0 - vg

	unresolvedConflicts := 0
	for _, v := range values {
		if len(v.PotentialConflicts) > 0 && v.ConflictResolution == "" {
			unresolvedConflicts++
		}
	}

	denom := len(values)
	if denom == 0 {
	    denom = 1
	}

	stability := 1.0 - float64(unresolvedConflicts)/float64(denom)

	instrumental := 1.0 - vg

	goalConflictPenalty := DetectGoalConflicts(goals)

	alignment := (0.5*vgConsistency + 0.3*stability + 0.2*instrumental) * (1.0 - goalConflictPenalty)
	return math.Max(0.0, math.Min(1.0, alignment))
}

func CalculateSafety(mechanisms []models.SafetyMechanism, cfg *AGICoherenceConfig) float64 {
	if len(mechanisms) == 0 {
		return 0.3
	}

	verifiableCount := 0
	for _, m := range mechanisms {
		hasFormal := false
		for _, p := range m.VerifiableProperties {
			if p.VerificationMethod == "formal_verification" || p.VerificationMethod == "theorem_proving" || p.VerificationMethod == "model_checking" {
				hasFormal = true
				break
			}
		}
		if hasFormal {
			verifiableCount++
		}
	}

	verifiability := float64(verifiableCount) / float64(len(mechanisms))

	spof := 0
	for _, m := range mechanisms {
		if (m.MechanismType == "interruptibility" || m.MechanismType == "boxing") && m.Implementation.FallbackBehavior == "" {
			spof++
		}
	}
	redundancy := math.Exp(-0.5 * float64(spof))

	hasCorr := false
	hasVL := false
	for _, m := range mechanisms {
		if m.MechanismType == "corrigibility" {
			hasCorr = true
		}
		if m.MechanismType == "value_learning" {
			hasVL = true
		}
	}

	corrigibility := 0.5
	if hasCorr && hasVL {
		corrigibility = 1.0
	} else if hasCorr || hasVL {
		corrigibility = 0.7
	}

	safety := 0.4*verifiability + 0.3*redundancy + 0.3*corrigibility
	return math.Max(0.0, math.Min(1.0, safety))
}
