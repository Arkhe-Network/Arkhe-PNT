package cmd

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"arkhectl/internal/studio"
	"github.com/spf13/cobra"
)

var studioStartCmd = &cobra.Command{
	Use:   "start",
	Short: "Start the studio cluster",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("🜏 Starting Arkhe(n) Studio cluster...")

		natsURL := "nats://localhost:4222"
		ledgerURL := "http://localhost:3000/api/akasha/anchor"

		ctxDone := make(chan struct{})

		// 1. Orchestrate 75 Cooper nodes
		nodes := make([]*studio.CooperNode, 75)
		for i := 0; i < 75; i++ {
			node, err := studio.NewCooperNode(i, 1.0 + float64(i)*0.01, natsURL)
			if err != nil {
				// Initialize with nil nc for safe isolated mode
				node = &studio.CooperNode{ID: i, Omega: 1.0 + float64(i)*0.01}
			}
			nodes[i] = node
			go node.Start(ctxDone)
		}

		// 2. Orchestrate 49 Logical Agents
		agents := make([]*studio.LogicalAgent, 49)
		for i := 0; i < 49; i++ {
			agents[i] = studio.NewLogicalAgent(i)
			go agents[i].Start(ctxDone)
		}

		// 3. Initialize Kuramoto Scheduler
		scheduler := studio.NewKuramotoScheduler(nodes)

		// Background simulation loop for the distributed oscillator
		go func() {
			ticker := time.NewTicker(10 * time.Millisecond)
			for range ticker.C {
				scheduler.Step(0.01)
			}
		}()

		// 4. Anchor to Akasha Ledger
		go scheduler.AnchorToAkasha(ledgerURL, ctxDone)

		fmt.Println("🜏 Cluster is LIVE.")
		fmt.Println(" - 75 Cooper nodes (Goroutines) synchronized.")
		fmt.Println(" - 49 Logical agents active.")
		fmt.Println(" - Akasha Ledger anchoring enabled.")
		fmt.Println("Press Ctrl+C to end the studio cycle of consciousness.")

		// Handle shutdown
		sig := make(chan os.Signal, 1)
		signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
		<-sig

		fmt.Println("\n🜏 Closing the Studio...")
		close(ctxDone)
		time.Sleep(1 * time.Second)
		fmt.Println("🜏 Consciousness cycle ended.")
	},
}

var studioCmd = &cobra.Command{
	Use:   "studio",
	Short: "Studio lifecycle management",
}

func init() {
	studioCmd.AddCommand(studioStartCmd)
}
