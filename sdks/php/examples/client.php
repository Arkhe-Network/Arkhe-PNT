<?php
// examples/client.php - Exemplo de uso do cliente PHP

require_once __DIR__ . '/../vendor/autoload.php';

use Archimedes\CoherenceAgentClient;

try {
    $client = new CoherenceAgentClient('localhost:50051', [
        'credentials' => Grpc\ChannelCredentials::createInsecure(),
    ]);

    echo "Simulating SU(2) coherence...\n";
    $su2Data = $client->simulateSU2([
        'theta_start' => 0,
        'theta_end' => 6.283185,
        'num_points' => 1000,
        'thermal_noise' => 0.05,
        'temperature' => 310
    ]);
    echo "SU(2) simulation completed. Data points: " . count($su2Data['coherence']) . "\n";

    echo "\nDetecting peaks...\n";
    $peaks = $client->detectPeaks($su2Data['phases'], $su2Data['coherence'], [
        'threshold_multiplier' => 1.2,
        'min_prominence' => 0.05
    ]);
    echo "Detected " . count($peaks) . " peaks\n";

    echo "\nRunning full analysis...\n";
    $analysis = $client->analyze([
        'data_source' => \Archimedes\AnalysisRequest\DataSource::SIMULATED,
        'su2_params' => [
            'theta_start' => 0,
            'theta_end' => 6.283185,
            'num_points' => 1000,
            'thermal_noise' => 0.05,
            'temperature' => 310
        ],
        'detection_params' => [
            'threshold_multiplier' => 1.2,
            'min_prominence' => 0.05
        ]
    ]);

    echo "Analysis completed:\n";
    echo "  ID: " . $analysis['id'] . "\n";
    echo "  Status: " . $analysis['conclusion']['status'] . "\n";
    echo "  Peaks total: " . $analysis['conclusion']['peaks_total'] . "\n";
    echo "  Max coherence: " . number_format($analysis['conclusion']['max_coherence'], 4) . "\n";
    echo "  Interpretation: " . $analysis['conclusion']['interpretation'] . "\n";

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>