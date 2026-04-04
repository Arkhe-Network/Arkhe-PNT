<?php
// src/CoherenceAgentClient.php - Cliente PHP para Agente Archimedes-Ω

namespace Archimedes;

use Grpc\ChannelCredentials;
use Archimedes\CoherenceAgentClient as GrpcClient;
use Archimedes\SU2Request;
use Archimedes\SL3ZRequest;
use Archimedes\PeakDetectionRequest;
use Archimedes\AnalysisRequest;
use Archimedes\ExperimentalData;
use Archimedes\DetectionParams;

class CoherenceAgentClient
{
    private $client;

    public function __construct(string $host = 'localhost:50051', array $options = [])
    {
        $credentials = $options['credentials'] ?? ChannelCredentials::createInsecure();
        $this->client = new GrpcClient($host, $options);
    }

    /**
     * Simula modelo de coerência SU(2) contínua
     */
    public function simulateSU2(array $params = []): array
    {
        $request = new SU2Request();
        $request->setThetaStart($params['theta_start'] ?? 0.0);
        $request->setThetaEnd($params['theta_end'] ?? 6.283185307179586);
        $request->setNumPoints($params['num_points'] ?? 1000);
        $request->setThermalNoise($params['thermal_noise'] ?? 0.05);
        $request->setTemperature($params['temperature'] ?? 310.0);

        list($response, $status) = $this->client->SimulateSU2($request)->wait();

        if ($status->code !== \Grpc\STATUS_OK) {
            throw new \Exception("gRPC error: " . $status->details);
        }

        return [
            'phases' => iterator_to_array($response->getPhases()),
            'coherence' => iterator_to_array($response->getCoherence())
        ];
    }

    /**
     * Simula modelo de coerência SL(3,ℤ) discreta
     */
    public function simulateSL3Z(array $params = []): array
    {
        $request = new SL3ZRequest();
        $request->setThetaStart($params['theta_start'] ?? 0.0);
        $request->setThetaEnd($params['theta_end'] ?? 6.283185307179586);
        $request->setNumPoints($params['num_points'] ?? 1000);

        $words = $params['words'] ?? ['e', 'a', 'b', 'ab', 'ba', 'aba'];
        foreach ($words as $word) {
            $request->addWords($word);
        }

        list($response, $status) = $this->client->SimulateSL3Z($request)->wait();

        if ($status->code !== \Grpc\STATUS_OK) {
            throw new \Exception("gRPC error: " . $status->details);
        }

        return [
            'phases' => iterator_to_array($response->getPhases()),
            'coherence' => iterator_to_array($response->getCoherence())
        ];
    }

    /**
     * Detecta picos nos dados de coerência
     */
    public function detectPeaks(array $phases, array $coherence, array $params = []): array
    {
        $request = new PeakDetectionRequest();
        foreach ($phases as $phase) {
            $request->addPhases($phase);
        }
        foreach ($coherence as $coh) {
            $request->addCoherence($coh);
        }
        $request->setThresholdMultiplier($params['threshold_multiplier'] ?? 1.2);
        $request->setMinProminence($params['min_prominence'] ?? 0.05);

        list($response, $status) = $this->client->DetectPeaks($request)->wait();

        if ($status->code !== \Grpc\STATUS_OK) {
            throw new \Exception("gRPC error: " . $status->details);
        }

        $peaks = [];
        foreach ($response->getPeaks() as $peak) {
            $peaks[] = [
                'phase' => $peak->getPhase(),
                'phase_degrees' => $peak->getPhaseDegrees(),
                'coherence' => $peak->getCoherence(),
                'prominence' => $peak->getProminence(),
                'is_resonance' => $peak->getIsResonance(),
                'index' => $peak->getIndex()
            ];
        }

        return $peaks;
    }

    /**
     * Executa análise completa
     */
    public function analyze(array $params = []): array
    {
        $request = new AnalysisRequest();
        $request->setDataSource($params['data_source'] ?? AnalysisRequest\DataSource::SIMULATED);

        // Parâmetros SU(2)
        if (isset($params['su2_params'])) {
            $su2 = new SU2Request();
            $su2->setThetaStart($params['su2_params']['theta_start'] ?? 0.0);
            $su2->setThetaEnd($params['su2_params']['theta_end'] ?? 6.283185307179586);
            $su2->setNumPoints($params['su2_params']['num_points'] ?? 1000);
            $su2->setThermalNoise($params['su2_params']['thermal_noise'] ?? 0.05);
            $su2->setTemperature($params['su2_params']['temperature'] ?? 310.0);
            $request->setSu2Params($su2);
        }

        // Parâmetros SL(3,ℤ)
        if (isset($params['sl3z_params'])) {
            $sl3z = new SL3ZRequest();
            $sl3z->setThetaStart($params['sl3z_params']['theta_start'] ?? 0.0);
            $sl3z->setThetaEnd($params['sl3z_params']['theta_end'] ?? 6.283185307179586);
            $sl3z->setNumPoints($params['sl3z_params']['num_points'] ?? 1000);
            $words = $params['sl3z_params']['words'] ?? ['e', 'a', 'b', 'ab', 'ba', 'aba'];
            foreach ($words as $word) {
                $sl3z->addWords($word);
            }
            $request->setSl3zParams($sl3z);
        }

        // Dados experimentais
        if (isset($params['experimental_data'])) {
            $exp = new ExperimentalData();
            foreach ($params['experimental_data']['phases'] as $phase) {
                $exp->addPhases($phase);
            }
            foreach ($params['experimental_data']['coherence'] as $coh) {
                $exp->addCoherence($coh);
            }
            $request->setExperimentalData($exp);
        }

        // Parâmetros de detecção
        $det = new DetectionParams();
        $det->setThresholdMultiplier($params['detection_params']['threshold_multiplier'] ?? 1.2);
        $det->setMinProminence($params['detection_params']['min_prominence'] ?? 0.05);
        $request->setDetectionParams($det);

        list($response, $status) = $this->client->Analyze($request)->wait();

        if ($status->code !== \Grpc\STATUS_OK) {
            throw new \Exception("gRPC error: " . $status->details);
        }

        $peaks = [];
        foreach ($response->getPeaks() as $peak) {
            $peaks[] = [
                'phase' => $peak->getPhase(),
                'phase_degrees' => $peak->getPhaseDegrees(),
                'coherence' => $peak->getCoherence(),
                'prominence' => $peak->getProminence(),
                'is_resonance' => $peak->getIsResonance(),
                'index' => $peak->getIndex()
            ];
        }

        return [
            'id' => $response->getId(),
            'timestamp' => $response->getTimestamp(),
            'data_source' => $response->getDataSource(),
            'peaks' => $peaks,
            'conclusion' => [
                'status' => $response->getConclusion()->getStatus(),
                'peaks_total' => $response->getConclusion()->getPeaksTotal(),
                'peaks_in_resonance' => $response->getConclusion()->getPeaksInResonance(),
                'max_coherence' => $response->getConclusion()->getMaxCoherence(),
                'interpretation' => $response->getConclusion()->getInterpretation(),
                'philosophical_note' => $response->getConclusion()->getPhilosophicalNote()
            ],
            'output_file' => $response->getOutputFile()
        ];
    }
}
?>