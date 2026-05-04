package cmd

import (
	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "arkhectl",
	Short: "Arkhe(n) Studio CLI",
	Long:  "CLI for orchestrating the Arkhe(n) Studio cluster and its Cooper nodes.",
}

func Execute() error {
	return rootCmd.Execute()
}

func init() {
	rootCmd.AddCommand(studioCmd)
}
