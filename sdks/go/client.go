// client.go - Cliente Go para Agente Archimedes-Ω
package main

import (
    "context"
    "log"
    "time"

    "google.golang.org/grpc"
    pb "github.com/arkhe/archimedes-agent/proto"
)

func main() {
    // Conectar ao servidor gRPC
    conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
    if err != nil {
        log.Fatalf("Failed to connect: %v", err)
    }
    defer conn.Close()

    client := pb.NewCoherenceAgentClient(conn)
    ctx, cancel := context.WithTimeout(context.Background(), time.Second*10)
    defer cancel()

    // Exemplo: Simular SU(2)
    log.Println("Simulating SU(2) coherence...")
    su2Resp, err := client.SimulateSU2(ctx, &pb.SU2Request{
        ThetaStart: 0,
        ThetaEnd:   6.283185,
        NumPoints:  1000,
        ThermalNoise: 0.05,
        Temperature:  310,
    })
    if err != nil {
        log.Fatalf("SU2 simulation failed: %v", err)
    }
    log.Printf("SU(2) simulation completed. Data points: %d", len(su2Resp.Coherence))

    // Exemplo: Detectar picos
    log.Println("Detecting peaks...")
    peakResp, err := client.DetectPeaks(ctx, &pb.PeakDetectionRequest{
        Phases:             su2Resp.Phases,
        Coherence:          su2Resp.Coherence,
        ThresholdMultiplier: 1.2,
        MinProminence:      0.05,
    })
    if err != nil {
        log.Fatalf("Peak detection failed: %v", err)
    }
    log.Printf("Detected %d peaks", len(peakResp.Peaks))

    // Exemplo: Análise completa
    log.Println("Running full analysis...")
    analysisResp, err := client.Analyze(ctx, &pb.AnalysisRequest{
        DataSource: pb.AnalysisRequest_SIMULATED,
        Su2Params: &pb.SU2Request{
            ThetaStart: 0,
            ThetaEnd:   6.283185,
            NumPoints:  1000,
            ThermalNoise: 0.05,
            Temperature:  310,
        },
        DetectionParams: &pb.DetectionParams{
            ThresholdMultiplier: 1.2,
            MinProminence:      0.05,
        },
    })
    if err != nil {
        log.Fatalf("Analysis failed: %v", err)
    }

    log.Printf("Analysis completed:")
    log.Printf("  ID: %s", analysisResp.Id)
    log.Printf("  Status: %s", analysisResp.Conclusion.Status)
    log.Printf("  Peaks total: %d", analysisResp.Conclusion.PeaksTotal)
    log.Printf("  Max coherence: %.4f", analysisResp.Conclusion.MaxCoherence)
}