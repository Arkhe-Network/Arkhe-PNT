// arkhe_os/integration/gradient_to_action_potential_mapper.go
package integration

import (
	"fmt"
	"math"
	"sync"
	"time"
)

// ─── CONSTANTES DO MAPEAMENTO GRADIENTE→POTENCIAL ───────

const (
	// GradientToVoltageScale fator de escala para converter gradiente para volts
	GradientToVoltageScale = 1e-6 // V por unidade de gradiente

	// ActionPotentialThreshold threshold para "disparo" de potencial de ação
	ActionPotentialThreshold = 0.1 // unidades de gradiente normalizado

	// RestingPotential potencial de repouso biológico [V]
	RestingPotential = -0.070 // -70 mV

	// PeakActionPotential pico de potencial de ação [V]
	PeakActionPotential = 0.030 // +30 mV

	// RefractoryPeriod período refratário após disparo [s]
	RefractoryPeriod = 0.002 // 2 ms
)

// ─── TIPOS FUNDAMENTAIS ─────────────────────────────────

// ActionPotential representa um potencial de ação gerado a partir de gradiente
type ActionPotential struct {
	PotentialID   string
	SourceGPU     string
	Timestamp     time.Time
	AmplitudeV    float64 // amplitude do potencial [V]
	Duration_ms   float64 // duração do pulso [ms]
	Frequency_Hz  float64 // frequência de disparo [Hz]
	GradientNorm  float64 // norma do gradiente original
	Fired         bool    // se atingiu threshold de disparo
}

// GradientToActionPotentialMapper converte gradientes de LLM em potenciais de ação
type GradientToActionPotentialMapper struct {
	mu sync.RWMutex

	// Configuração
	scaleFactor     float64
	fireThreshold   float64
	restingPotential float64
	peakPotential   float64

	// Histórico de potenciais gerados
	potentialHistory []ActionPotential

	// Estado de disparo por GPU (para período refratário)
	firingState map[string]FiringState

	// Métricas
	metrics MapperMetrics
}

// FiringState rastreia estado de disparo de uma GPU
type FiringState struct {
	LastFireTime    time.Time
	ConsecutiveFires int
	RefractoryUntil time.Time
}

// MapperMetrics contém métricas do mapeador
type MapperMetrics struct {
	GradientsProcessed  int64   `json:"gradients_processed"`
	PotentialsGenerated int64   `json:"potentials_generated"`
	FiringRate_Hz       float64 `json:"firing_rate_Hz"`
	AvgAmplitude_mV     float64 `json:"avg_amplitude_mV"`
}

// ─── CONSTRUTORES ───────────────────────────────────────

// NewGradientToActionPotentialMapper cria novo mapeador
func NewGradientToActionPotentialMapper(config map[string]float64) *GradientToActionPotentialMapper {
	mapper := &GradientToActionPotentialMapper{
		scaleFactor:      config["scale_factor"],
		fireThreshold:    config["fire_threshold"],
		restingPotential: RestingPotential,
		peakPotential:    PeakActionPotential,
		firingState:      make(map[string]FiringState),
	}

	// Valores padrão se não configurados
	if mapper.scaleFactor == 0 {
		mapper.scaleFactor = GradientToVoltageScale
	}
	if mapper.fireThreshold == 0 {
		mapper.fireThreshold = ActionPotentialThreshold
	}

	return mapper
}

// MapGradientToPotential converte gradiente em potencial de ação
func (m *GradientToActionPotentialMapper) MapGradientToPotential(
	gpuID string,
	gradient []float64,
	timestamp time.Time,
) *ActionPotential {
	// Calcular norma do gradiente
	gradNorm := computeL2Norm(gradient)

	// Normalizar gradiente para faixa [0, 1]
	normalized := normalizeGradient(gradNorm)

	// Verificar período refratário
	if m.isInRefractoryPeriod(gpuID) {
		return &ActionPotential{
			PotentialID:  fmt.Sprintf("pot_%s_%d", gpuID[:8], timestamp.UnixNano()),
			SourceGPU:    gpuID,
			Timestamp:    timestamp,
			AmplitudeV:   m.restingPotential,
			Fired:        false,
			GradientNorm: gradNorm,
		}
	}

	// Verificar se atinge threshold de disparo
	fired := normalized >= m.fireThreshold

	var amplitude float64
	if fired {
		// Amplitude proporcional à magnitude do gradiente
		amplitude = m.restingPotential + (m.peakPotential-m.restingPotential)*normalized
		m.updateFiringState(gpuID, true)
	} else {
		amplitude = m.restingPotential
		m.updateFiringState(gpuID, false)
	}

	// Criar potencial de ação
	potential := &ActionPotential{
		PotentialID:   fmt.Sprintf("pot_%s_%d", gpuID[:8], timestamp.UnixNano()),
		SourceGPU:     gpuID,
		Timestamp:     timestamp,
		AmplitudeV:    amplitude,
		Duration_ms:   1.0, // simplificação: duração fixa
		Frequency_Hz:  m.computeFiringRate(gpuID),
		GradientNorm:  gradNorm,
		Fired:         fired,
	}

	// Atualizar histórico e métricas
	m.mu.Lock()
	m.potentialHistory = append(m.potentialHistory, *potential)
	if len(m.potentialHistory) > 10000 {
		m.potentialHistory = m.potentialHistory[1000:]
	}
	m.metrics.GradientsProcessed++
	if fired {
		m.metrics.PotentialsGenerated++
	}
	m.mu.Unlock()

	return potential
}

// computeL2Norm calcula norma L2 de vetor
func computeL2Norm(vec []float64) float64 {
	sum := 0.0
	for _, v := range vec {
		sum += v * v
	}
	return math.Sqrt(sum)
}

// normalizeGradient normaliza gradiente para faixa [0, 1]
func normalizeGradient(norm float64) float64 {
	// Função sigmoide para normalização suave
	return 1.0 / (1.0 + math.Exp(-norm*10.0 + 5.0))
}

// isInRefractoryPeriod verifica se GPU está em período refratário
func (m *GradientToActionPotentialMapper) isInRefractoryPeriod(gpuID string) bool {
	m.mu.RLock()
	defer m.mu.RUnlock()

	state, exists := m.firingState[gpuID]
	if !exists {
		return false
	}
	return time.Now().Before(state.RefractoryUntil)
}

// updateFiringState atualiza estado de disparo de GPU
func (m *GradientToActionPotentialMapper) updateFiringState(gpuID string, fired bool) {
	m.mu.Lock()
	defer m.mu.Unlock()

	state := m.firingState[gpuID]
	now := time.Now()

	if fired {
		state.LastFireTime = now
		state.ConsecutiveFires++
		state.RefractoryUntil = now.Add(time.Duration(RefractoryPeriod * 1e9) * time.Nanosecond)
	} else {
		state.ConsecutiveFires = 0
	}

	m.firingState[gpuID] = state
}

// computeFiringRate calcula taxa de disparo recente para GPU
func (m *GradientToActionPotentialMapper) computeFiringRate(gpuID string) float64 {
	m.mu.RLock()
	defer m.mu.RUnlock()

	state := m.firingState[gpuID]
	if state.ConsecutiveFires == 0 {
		return 0.0
	}

	// Taxa baseada em disparos recentes (janela de 1 segundo)
	windowStart := time.Now().Add(-1 * time.Second)
	count := 0
	for _, pot := range m.potentialHistory {
		if pot.SourceGPU == gpuID && pot.Timestamp.After(windowStart) && pot.Fired {
			count++
		}
	}

	return float64(count) // Hz
}

// GetMapperMetrics retorna métricas consolidadas do mapeador
func (m *GradientToActionPotentialMapper) GetMapperMetrics() MapperMetrics {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.metrics
}
