// arkhe_os/integration/datacenter_em_coherence_monitor.go
package integration

import (
	"context"
	"fmt"
	"math"
	"math/cmplx"
	"sync"
	"time"

	"arkhe_os/sensors"
	"arkhe_os/photonic"
)

// ─── CONSTANTES DE COERÊNCIA EM DE DATA CENTERS ───────────

const (
	// EMCoherenceThreshold limiar mínimo para promoção a nó sináptico
	EMCoherenceThreshold = 0.70

	// EMCoherenceSamplingRate taxa de amostragem de medições EM [Hz]
	EMCoherenceSamplingRate = 10.0

	// PhaseCorrelationWindow janela temporal para correlação de fase [s]
	PhaseCorrelationWindow = 5.0

	// MinGPUsForCoherence mínimo de GPUs para cálculo significativo de coerência
	MinGPUsForCoherence = 16

	// EMAttenuationFactor fator de atenuação por blindagem do data center [1/m]
	EMAttenuationFactor = 0.05
)

// ─── TIPOS FUNDAMENTAIS ───────────────────────────────────

// GPUComponent representa uma GPU no cluster com seus parâmetros EM
type GPUComponent struct {
	GPUID          string
	Position       [3]float64    // posição física no data center [m]
	ClockFrequency float64       // frequência de clock efetiva [Hz]
	PowerDrawW     float64       // consumo de potência [W]
	PhaseOffset    float64       // fase relativa do padrão de computação [rad]
	ActivityLevel  float64       // nível de atividade [0, 1]
}

// EMFieldSnapshot representa um snapshot do campo EM do cluster
type EMFieldSnapshot struct {
	SnapshotID    string
	Timestamp     time.Time
	ClusterID     string
	FieldStrength float64           // |E| médio no cluster [V/m]
	PhaseCoherence float64          // Φ_C^DC calculado [0, 1]
	GPUCount      int
	TotalPowerMW  float64
	DominantFreq  float64           // frequência dominante do campo [Hz]
	Metadata      map[string]interface{}
}

// EMCoherenceMonitor monitora coerência eletromagnética de data centers
type EMCoherenceMonitor struct {
	mu sync.RWMutex

	// Identificação
	monitorID   string
	clusterID   string
	datacenter  string

	// Sensores integrados (Substratos 152 + 162)
	geomagSensor *sensors.GeomagneticSensor
	metasurface  *photonic.GrapheneMetasurface

	// Componentes do cluster
	gpuComponents map[string]*GPUComponent

	// Histórico de medições
	snapshotHistory []EMFieldSnapshot

	// Callbacks para promoção de nós
	promotionCallbacks []func(string, float64)

	// Métricas de monitoramento
	metrics MonitorMetrics
	config  MonitorConfig
}

// MonitorMetrics contém métricas do monitor de coerência EM
type MonitorMetrics struct {
	SnapshotsCaptured     int64   `json:"snapshots_captured"`
	PromotionsTriggered   int64   `json:"promotions_triggered"`
	AvgPhaseCoherence     float64 `json:"avg_phase_coherence"`
	PeakFieldStrengthVm   float64 `json:"peak_field_strength_Vm"`
	GPUsMonitored         int64   `json:"gpus_monitored"`
	LastCoherenceValue    float64 `json:"last_coherence_value"`
}

// MonitorConfig contém configuração do monitor
type MonitorConfig struct {
	EnableGeomagSensor    bool
	EnableMetasurface     bool
	CoherenceThreshold    float64
	PromotionHysteresis   float64 // para evitar oscilação de promoção
	SamplingIntervalSec   float64
	PhaseCorrelationWindowSec float64
}

// ─── CONSTRUTORES ─────────────────────────────────────────

// NewEMCoherenceMonitor cria novo monitor para data center
func NewEMCoherenceMonitor(
	monitorID string,
	clusterID string,
	datacenter string,
	config MonitorConfig,
) (*EMCoherenceMonitor, error) {
	if config.CoherenceThreshold == 0 {
		config.CoherenceThreshold = EMCoherenceThreshold
	}
	if config.SamplingIntervalSec == 0 {
		config.SamplingIntervalSec = 1.0 / EMCoherenceSamplingRate
	}

	monitor := &EMCoherenceMonitor{
		monitorID:     monitorID,
		clusterID:     clusterID,
		datacenter:    datacenter,
		gpuComponents: make(map[string]*GPUComponent),
		config:        config,
	}

	// Inicializar sensores se habilitados
	if config.EnableGeomagSensor {
		monitor.geomagSensor = sensors.NewGeomagneticSensor(
			fmt.Sprintf("geomag_%s", monitorID),
			sensors.SensorConfig{SamplingRate: EMCoherenceSamplingRate},
		)
	}

	if config.EnableMetasurface {
		monitor.metasurface = photonic.NewGrapheneMetasurface(
			fmt.Sprintf("meta_%s", monitorID),
			photonic.MetasurfaceConfig{
				FermiLevel_eV: 0.5,
				TargetFrequency: 1.0e12, // 1 THz para detecção de harmônicos
			},
		)
	}

	return monitor, nil
}

// RegisterGPUComponent registra GPU para monitoramento EM
func (m *EMCoherenceMonitor) RegisterGPUComponent(gpu *GPUComponent) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.gpuComponents[gpu.GPUID] = gpu
	m.metrics.GPUsMonitored = int64(len(m.gpuComponents))
}

// ─── OPERAÇÕES DE MEDIÇÃO DE COERÊNCIA EM ─────────────────

// CaptureEMSnapshot captura snapshot do campo EM do cluster
func (m *EMCoherenceMonitor) CaptureEMSnapshot(ctx context.Context) (*EMFieldSnapshot, error) {
	m.mu.RLock()
	if len(m.gpuComponents) < MinGPUsForCoherence {
		m.mu.RUnlock()
		return nil, fmt.Errorf("insufficient GPUs for coherence measurement: %d < %d",
			len(m.gpuComponents), MinGPUsForCoherence)
	}
	gpus := make([]*GPUComponent, 0, len(m.gpuComponents))
	for _, gpu := range m.gpuComponents {
		gpus = append(gpus, gpu)
	}
	m.mu.RUnlock()

	// Coletar medições de sensores se disponíveis
	var geomagReading, metasurfaceReading float64
	if m.geomagSensor != nil {
		reading, _ := m.geomagSensor.ReadField(ctx)
		geomagReading = reading.FieldStrength
	}
	if m.metasurface != nil {
		reading, _ := m.metasurface.SenseElectricCoherence(1.0) // campo simulado
		metasurfaceReading = reading
	}

	// Calcular coerência de fase entre GPUs
	phaseCoherence := m.computePhaseCoherence(gpus)

	// Calcular intensidade de campo médio
	fieldStrength := m.computeAverageFieldStrength(gpus, geomagReading, metasurfaceReading)

	// Encontrar frequência dominante (simplificação: média ponderada por potência)
	dominantFreq := m.computeDominantFrequency(gpus)

	// Calcular potência total
	var totalPowerMW float64
	for _, gpu := range gpus {
		totalPowerMW += gpu.PowerDrawW / 1e6
	}

	// Criar snapshot
	snapshot := &EMFieldSnapshot{
		SnapshotID:     fmt.Sprintf("em_%s_%d", m.clusterID[:8], time.Now().UnixNano()),
		Timestamp:      time.Now(),
		ClusterID:      m.clusterID,
		FieldStrength:  fieldStrength,
		PhaseCoherence: phaseCoherence,
		GPUCount:       len(gpus),
		TotalPowerMW:   totalPowerMW,
		DominantFreq:   dominantFreq,
		Metadata: map[string]interface{}{
			"geomag_reading":  geomagReading,
			"metasurface_reading": metasurfaceReading,
			"datacenter": m.datacenter,
		},
	}

	// Atualizar histórico e métricas
	m.mu.Lock()
	m.snapshotHistory = append(m.snapshotHistory, *snapshot)
	if len(m.snapshotHistory) > 1000 {
		m.snapshotHistory = m.snapshotHistory[1:]
	}
	m.metrics.SnapshotsCaptured++
	m.metrics.AvgPhaseCoherence = m.metrics.AvgPhaseCoherence*0.99 + phaseCoherence*0.01
	m.metrics.PeakFieldStrengthVm = math.Max(m.metrics.PeakFieldStrengthVm, fieldStrength)
	m.metrics.LastCoherenceValue = phaseCoherence
	m.mu.Unlock()

	// Verificar se atingiu limiar para promoção
	if phaseCoherence >= m.config.CoherenceThreshold {
		m.checkPromotionThreshold(snapshot)
	}

	return snapshot, nil
}

// computePhaseCoherence calcula Φ_C^DC via correlação de fase entre GPUs
func (m *EMCoherenceMonitor) computePhaseCoherence(gpus []*GPUComponent) float64 {
	if len(gpus) < 2 {
		return 0.0
	}

	// Calcular soma de correlações de fase ponderadas por distância
	var sumComplex complex128
	var totalWeight float64

	for i, gpuA := range gpus {
		for j, gpuB := range gpus {
			if i >= j {
				continue
			}

			// Diferença de fase
			phaseDiff := gpuA.PhaseOffset - gpuB.PhaseOffset

			// Peso por proximidade espacial (decai com distância)
			dx := gpuA.Position[0] - gpuB.Position[0]
			dy := gpuA.Position[1] - gpuB.Position[1]
			dz := gpuA.Position[2] - gpuB.Position[2]
			distance := math.Sqrt(dx*dx + dy*dy + dz*dz)
			weight := math.Exp(-distance * EMAttenuationFactor)

			// Contribuição para coerência
			sumComplex += cmplx.Exp(complex(0, phaseDiff)) * complex(weight, 0)
			totalWeight += weight
		}
	}

	if totalWeight < 1e-10 {
		return 0.0
	}

	// Coerência = magnitude da média ponderada de fasores
	coherence := cmplx.Abs(sumComplex) / totalWeight
	return math.Max(0.0, math.Min(1.0, coherence))
}

// computeAverageFieldStrength calcula intensidade média de campo EM
func (m *EMCoherenceMonitor) computeAverageFieldStrength(
	gpus []*GPUComponent,
	geomagReading, metasurfaceReading float64,
) float64 {
	// Contribuição de cada GPU baseada em potência e atividade
	var totalField float64
	for _, gpu := range gpus {
		// Campo proporcional a sqrt(potência) * nível de atividade
		gpuField := math.Sqrt(gpu.PowerDrawW) * gpu.ActivityLevel * 0.01 // fator de escala
		totalField += gpuField
	}

	// Média com leituras de sensores se disponíveis
	sensorWeight := 0.0
	if geomagReading > 0 {
		totalField += geomagReading * 100 // converter unidades
		sensorWeight += 0.3
	}
	if metasurfaceReading > 0 {
		totalField += metasurfaceReading * 50
		sensorWeight += 0.3
	}

	if sensorWeight > 0 {
		totalField /= (1.0 + sensorWeight)
	} else if len(gpus) > 0 {
		totalField /= float64(len(gpus))
	}

	return totalField
}

// computeDominantFrequency encontra frequência dominante do campo
func (m *EMCoherenceMonitor) computeDominantFrequency(gpus []*GPUComponent) float64 {
	if len(gpus) == 0 {
		return 0.0
	}

	// Média ponderada por potência de clock das GPUs
	var weightedSum, totalWeight float64
	for _, gpu := range gpus {
		weight := gpu.PowerDrawW * gpu.ActivityLevel
		weightedSum += gpu.ClockFrequency * weight
		totalWeight += weight
	}

	if totalWeight < 1e-10 {
		return 0.0
	}
	return weightedSum / totalWeight
}

// checkPromotionThreshold verifica se data center deve ser promovido a nó
func (m *EMCoherenceMonitor) checkPromotionThreshold(snapshot *EMFieldSnapshot) {
	// Aplicar histerese para evitar oscilação
	if snapshot.PhaseCoherence >= m.config.CoherenceThreshold+m.config.PromotionHysteresis {
		// Disparar callbacks de promoção
		for _, cb := range m.promotionCallbacks {
			cb(m.clusterID, snapshot.PhaseCoherence)
		}
		m.metrics.PromotionsTriggered++
	}
}

// RegisterPromotionCallback registra callback para eventos de promoção
func (m *EMCoherenceMonitor) RegisterPromotionCallback(
	cb func(clusterID string, coherence float64),
) {
	m.promotionCallbacks = append(m.promotionCallbacks, cb)
}

// GetMonitorMetrics retorna métricas consolidadas do monitor
func (m *EMCoherenceMonitor) GetMonitorMetrics() MonitorMetrics {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.metrics
}

// StartContinuousMonitoring inicia loop de monitoramento contínuo
func (m *EMCoherenceMonitor) StartContinuousMonitoring(ctx context.Context) {
	ticker := time.NewTicker(time.Duration(m.config.SamplingIntervalSec * 1e9) * time.Nanosecond)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			_, err := m.CaptureEMSnapshot(ctx)
			if err != nil {
				// Logar erro mas continuar loop
				continue
			}
		}
	}
}
