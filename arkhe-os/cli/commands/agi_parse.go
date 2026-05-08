// cli/commands/agi_parse.go
package commands

import (
	"fmt"
	"os"
	"path/filepath"

	"arkhe/parser/frontends/agi"
	"arkhe/parser/lfir"
	"github.com/spf13/cobra"
)

var AgiParseCmd = &cobra.Command{
	Use:   "agi-parse --file <spec.yaml|json>",
	Short: "Parse AGI system specifications into LFIR graphs with coherence metrics",
	Long: `Analyze AGI system specifications for architectural coherence, value alignment, and safety robustness.

Supported inputs:
  • YAML or JSON specifications defining values, goals, modules, and safety mechanisms.

Key analyses:
  • Value Alignment: Analyzes instrumental risk and goal conflicts.
  • Architectural Coherence: Analyzes module integration.
  • Safety Robustness: Analyzes verifiable properties and fallback behaviors.

Examples:
  arkhe agi parse --file spec.yaml
  arkhe agi parse --file spec.json --output lfir.json`,
	RunE: runAgiParse,
}

var (
	agiFile    string
	agiOutput  string
	agiVerbose bool
)

func init() {
	AgiParseCmd.Flags().StringVarP(&agiFile, "file", "f", "", "Path to AGI specification file (required)")
	AgiParseCmd.Flags().StringVarP(&agiOutput, "output", "o", "", "Output path for LFIR JSON")
	AgiParseCmd.Flags().BoolVarP(&agiVerbose, "verbose", "v", false, "Verbose output with detailed metrics")
	AgiParseCmd.MarkFlagRequired("file")
}

func runAgiParse(cmd *cobra.Command, args []string) error {
	if agiFile == "" {
		return fmt.Errorf("--file is required")
	}

	source, err := os.ReadFile(agiFile)
	if err != nil {
		return fmt.Errorf("failed to read file: %w", err)
	}

	parser := agi.NewAGIParser()

	graph, err := parser.Parse(source, filepath.Base(agiFile), nil)
	if err != nil {
		return fmt.Errorf("parse failed: %w", err)
	}

	if agiVerbose {
		fmt.Printf("🧠 ARKHE AGI Analysis — %s\n", filepath.Base(agiFile))
		fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
		printAgiStats(graph)
	}

	if agiOutput != "" {
		if err := graph.ToJSONFile(agiOutput); err != nil {
			return fmt.Errorf("failed to write output: %w", err)
		}
		fmt.Printf("✅ LFIR graph saved to %s\n", agiOutput)
	}

	coherence := graph.Metrics.CoherenceScore
	status := "✅"
	if coherence < 0.7 {
		status = "⚠️"
	}
	if coherence < 0.5 {
		status = "❌"
	}
	fmt.Printf("• Φ_C (AGI System Coherence) = %.2f %s\n", coherence, status)

	root := graph.Nodes[graph.RootNodes[0]]
	if emergenceRisks, ok := root.Attributes["emergence_risks"].(int); ok && emergenceRisks > 0 {
		fmt.Printf("⚠️  %d emergence risk(s) detected\n", emergenceRisks)
	}
	if conflictingGoals, ok := root.Attributes["conflicting_goals"].(int); ok && conflictingGoals > 0 {
		fmt.Printf("⚠️  Conflicting goals detected in specification\n")
	}
	if valueContradictions, ok := root.Attributes["value_contradictions"].(int); ok && valueContradictions > 0 {
		fmt.Printf("⚠️  %d unresolved value contradiction(s) found\n", valueContradictions)
	}

	return nil
}

func printAgiStats(graph *lfir.LFIRGraph) {
	root := graph.Nodes[graph.RootNodes[0]]

	fmt.Printf("• System Name: %s\n", root.Attributes["system_name"])
	fmt.Printf("• Architecture: %s\n", root.Attributes["architecture_type"])
	fmt.Printf("• Modules: %d\n", root.Attributes["module_count"])
	fmt.Printf("• Goals: %d\n", root.Attributes["goal_count"])
	fmt.Printf("• Values: %d\n", root.Attributes["value_count"])
	fmt.Printf("• Safety Mechanisms: %d\n", root.Attributes["safety_mechanism_count"])

	if root.Attributes["coherence_architecture"] != nil {
		fmt.Printf("\nCoherence Components:\n")
		fmt.Printf("  • Architecture: %.2f\n", root.Attributes["coherence_architecture"])
		fmt.Printf("  • Alignment: %.2f\n", root.Attributes["coherence_alignment"])
		fmt.Printf("  • Safety: %.2f\n", root.Attributes["coherence_safety"])

		if metaCog := root.Attributes["coherence_meta_cognition"]; metaCog != nil {
			fmt.Printf("  • Meta-Cognition: %.2f\n", metaCog)
		}
	}
}
