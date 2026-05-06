package main

import (
	"encoding/json"
	"fmt"
	"math"
	"strings"
	"sync"
	"time"
)

// ─── CONSTANTES DO ESPECTRO HARMÔNICO δ ───────────────────────────

const (
	// Constantes fundamentais do espectro δ
	Constant108 = 108.0                 // Distância Terra-Sol / diâmetro solar
	Constant137 = 137.035999084         // Constante de estrutura fina α⁻¹
	ConstantPhi = 1.6180339887498948482 // Razão áurea φ
	Constant26  = 26.0                  // Dimensão crítica da teoria bosônica de cordas
	Constant153 = 153.0                 // Número de peixes / supply máximo
	Constant248 = 248.0                 // Dimensão do grupo de Lie excepcional E₈

	// Faixa saudável de δ
	DeltaHealthyMin = 0.04
	DeltaHealthyMax = 0.10

	// Fatores de calibração
	CalibrationSensitivity   = 0.01
	MaxCalibrationAdjustment = 0.5
)

// HarmonicConstant representa uma constante do espectro δ
type HarmonicConstant struct {
	Name         string
	Value        float64
	Description  string
	Applications []string // Domínios de aplicação
}

// SubstrateParameter representa um parâmetro calibrável de um substrato
type SubstrateParameter struct {
	Name            string
	SubstrateID     int
	CurrentValue    float64
	MinValue        float64
	MaxValue        float64
	CalibrationFunc string  // Nome da função de calibração harmônica
	ContextWeight   float64 // Peso do contexto na calibração
}

// CosmicHarmonicCalibrator calibra parâmetros de substratos usando o espectro δ
type CosmicHarmonicCalibrator struct {
	mu sync.RWMutex

	// Espectro harmônico δ
	harmonicConstants map[string]*HarmonicConstant

	// Parâmetros calibráveis por substrato
	calibratableParams map[int][]*SubstrateParameter

	// Contexto operacional atual
	operationalContext map[string]float64

	// Histórico de calibrações
	calibrationHistory []CalibrationRecord

	// Callbacks para notificação de calibrações
	calibrationCallbacks []func(CalibrationRecord)

	// Métricas de calibração
	metrics CalibratorMetrics
}

// CalibrationRecord registra uma calibração realizada
type CalibrationRecord struct {
	Timestamp     time.Time
	SubstrateID   int
	ParamName     string
	OldValue      float64
	NewValue      float64
	ConstantsUsed []string
	Context       map[string]float64
	Justification string
}

// CalibratorMetrics contém métricas do calibrador cósmico
type CalibratorMetrics struct {
	CalibrationsPerformed  int64   `json:"calibrations_performed"`
	AvgAdjustmentMagnitude float64 `json:"avg_adjustment_magnitude"`
	ParamsCalibrated       int     `json:"params_calibrated"`
	HarmonicResonanceScore float64 `json:"harmonic_resonance_score"`
}

// ─── CONSTRUTORES ─────────────────────────────────────────────────

// NewCosmicHarmonicCalibrator cria novo calibrador cósmico
func NewCosmicHarmonicCalibrator() *CosmicHarmonicCalibrator {
	cal := &CosmicHarmonicCalibrator{
		harmonicConstants:  make(map[string]*HarmonicConstant),
		calibratableParams: make(map[int][]*SubstrateParameter),
		operationalContext: make(map[string]float64),
	}

	// Registrar constantes do espectro δ
	cal.registerHarmonicConstants()

	// Registrar parâmetros calibráveis padrão
	cal.registerDefaultCalibratableParams()

	return cal
}

// registerHarmonicConstants registra as constantes do espectro δ
func (c *CosmicHarmonicCalibrator) registerHarmonicConstants() {
	c.harmonicConstants["108"] = &HarmonicConstant{
		Name: "108", Value: Constant108,
		Description:  "Distância Terra-Sol / diâmetro solar; ciclos cósmicos",
		Applications: []string{"temporal_scaling", "cyclic_processes", "addressing"},
	}
	c.harmonicConstants["137"] = &HarmonicConstant{
		Name: "137", Value: Constant137,
		Description:  "Constante de estrutura fina α⁻¹; acoplamento eletromagnético",
		Applications: []string{"em_coupling", "quantum_interactions", "field_strength"},
	}
	c.harmonicConstants["phi"] = &HarmonicConstant{
		Name: "phi", Value: ConstantPhi,
		Description:  "Razão áurea φ; crescimento ótimo, proporções harmônicas",
		Applications: []string{"optimization", "scaling", "aesthetic_balance"},
	}
	c.harmonicConstants["26"] = &HarmonicConstant{
		Name: "26", Value: Constant26,
		Description:  "Dimensão crítica da teoria bosônica de cordas",
		Applications: []string{"dimensional_reduction", "string_theory", "compactification"},
	}
	c.harmonicConstants["153"] = &HarmonicConstant{
		Name: "153", Value: Constant153,
		Description:  "Número de peixes; supply máximo, completude",
		Applications: []string{"resource_limits", "tokenomics", "completion_thresholds"},
	}
	c.harmonicConstants["248"] = &HarmonicConstant{
		Name: "248", Value: Constant248,
		Description:  "Dimensão de E₈; simetria máxima, unificação",
		Applications: []string{"symmetry_groups", "unification", "state_space_dim"},
	}
}

// registerDefaultCalibratableParams registra parâmetros padrão calibráveis
func (c *CosmicHarmonicCalibrator) registerDefaultCalibratableParams() {
	// Exemplo: parâmetros do CoherenceRouter (Substrato 171)
	c.calibratableParams[171] = []*SubstrateParameter{
		{
			Name: "coherence_threshold", SubstrateID: 171,
			CurrentValue: 0.85, MinValue: 0.5, MaxValue: 0.99,
			CalibrationFunc: "phi_weighted", ContextWeight: 0.7,
		},
		{
			Name: "temporal_flex_factor", SubstrateID: 171,
			CurrentValue: 1.0, MinValue: 0.1, MaxValue: 10.0,
			CalibrationFunc: "harmonic_series", ContextWeight: 0.5,
		},
	}

	// Exemplo: parâmetros do OAMTransceiver (Substrato 185)
	c.calibratableParams[185] = []*SubstrateParameter{
		{
			Name: "carrier_frequency_base", SubstrateID: 185,
			CurrentValue: 19.7e12, MinValue: 1e9, MaxValue: 1e15,
			CalibrationFunc: "fine_structure_scaled", ContextWeight: 0.9,
		},
		{
			Name: "mode_count", SubstrateID: 185,
			CurrentValue: 7, MinValue: 1, MaxValue: 26,
			CalibrationFunc: "dimensional_harmonic", ContextWeight: 0.3,
		},
	}
}

// ─── OPERAÇÕES DE CALIBRAÇÃO CÓSMICA ─────────────────────────────

// SetOperationalContext define o contexto operacional para calibração
func (c *CosmicHarmonicCalibrator) SetOperationalContext(context map[string]float64) {
	c.mu.Lock()
	defer c.mu.Unlock()
	for k, v := range context {
		c.operationalContext[k] = v
	}
}

// CalibrateParameter calibra um parâmetro específico usando o espectro δ
func (c *CosmicHarmonicCalibrator) CalibrateParameter(
	substrateID int,
	paramName string,
	force bool,
) (*SubstrateParameter, error) {
	c.mu.Lock()
	defer c.mu.Unlock()

	params, exists := c.calibratableParams[substrateID]
	if !exists {
		return nil, fmt.Errorf("no calibratable params for substrate %d", substrateID)
	}

	var targetParam *SubstrateParameter
	for _, p := range params {
		if p.Name == paramName {
			targetParam = p
			break
		}
	}
	if targetParam == nil {
		return nil, fmt.Errorf("parameter %s not found in substrate %d", paramName, substrateID)
	}

	oldValue := targetParam.CurrentValue

	// Aplicar função de calibração harmônica
	newValue, constantsUsed, justification := c.applyHarmonicCalibration(
		targetParam, c.operationalContext,
	)

	// Validar limites
	newValue = math.Max(targetParam.MinValue, math.Min(targetParam.MaxValue, newValue))

	// Aplicar ajuste se significativo ou forçado
	if force || math.Abs(newValue-oldValue) > CalibrationSensitivity {
		record := CalibrationRecord{
			Timestamp:     time.Now(),
			SubstrateID:   substrateID,
			ParamName:     paramName,
			OldValue:      oldValue,
			NewValue:      newValue,
			ConstantsUsed: constantsUsed,
			Context:       copyMap(c.operationalContext),
			Justification: justification,
		}

		targetParam.CurrentValue = newValue
		c.calibrationHistory = append(c.calibrationHistory, record)
		c.metrics.CalibrationsPerformed++

		// Atualizar métricas
		adjustment := math.Abs(newValue-oldValue) / oldValue
		n := c.metrics.CalibrationsPerformed
		oldAvg := c.metrics.AvgAdjustmentMagnitude
		c.metrics.AvgAdjustmentMagnitude = (oldAvg*float64(n-1) + adjustment) / float64(n)

		// Notificar callbacks
		for _, cb := range c.calibrationCallbacks {
			cb(record)
		}

		return targetParam, nil
	}

	return targetParam, nil
}

// applyHarmonicCalibration aplica função de calibração baseada em constantes harmônicas
func (c *CosmicHarmonicCalibrator) applyHarmonicCalibration(
	param *SubstrateParameter,
	context map[string]float64,
) (newValue float64, constantsUsed []string, justification string) {

	switch param.CalibrationFunc {
	case "phi_weighted":
		// Calibração ponderada pela razão áurea
		phi := c.harmonicConstants["phi"].Value
		contextWeight := param.ContextWeight * context["criticality"]
		newValue = param.CurrentValue * (1.0 + (phi-1.0)*contextWeight*0.1)
		constantsUsed = []string{"phi"}
		justification = fmt.Sprintf("φ-weighted adjustment for criticality %.2f", contextWeight)

	case "harmonic_series":
		// Série harmônica baseada em múltiplas constantes
		sum := 0.0
		for _, name := range []string{"108", "137", "phi", "26"} {
			if constVal, ok := c.harmonicConstants[name]; ok {
				sum += constVal.Value / 100.0 // Normalizar
			}
		}
		adjustment := (sum / 4.0) * CalibrationSensitivity * context["temporal_scale"]
		newValue = param.CurrentValue * (1.0 + adjustment)
		constantsUsed = []string{"108", "137", "phi", "26"}
		justification = "harmonic series average applied"

	case "fine_structure_scaled":
		// Escalonamento pela constante de estrutura fina
		alpha := 1.0 / c.harmonicConstants["137"].Value
		scaleFactor := math.Pow(alpha, context["em_environment"])
		newValue = param.CurrentValue * scaleFactor
		constantsUsed = []string{"137"}
		justification = fmt.Sprintf("fine-structure scaling: α^%.3f", context["em_environment"])

	case "dimensional_harmonic":
		// Harmônico dimensional baseado em 26 e 248
		dim26 := c.harmonicConstants["26"].Value
		dim248 := c.harmonicConstants["248"].Value
		ratio := dim248 / dim26 // ~9.54
		targetModes := int(math.Round(ratio * context["complexity"]))
		newValue = float64(targetModes)
		constantsUsed = []string{"26", "248"}
		justification = fmt.Sprintf("dimensional harmonic: E₈/SO(26) ratio × complexity")

	default:
		// Fallback: ajuste mínimo baseado em φ
		phi := c.harmonicConstants["phi"].Value
		newValue = param.CurrentValue * (1.0 + (phi-1.0)*CalibrationSensitivity)
		constantsUsed = []string{"phi"}
		justification = "default φ-minimal adjustment"
	}

	return newValue, constantsUsed, justification
}

// CalibrateAllParameters calibra todos os parâmetros registráveis
func (c *CosmicHarmonicCalibrator) CalibrateAllParameters(force bool) map[int][]*SubstrateParameter {
	results := make(map[int][]*SubstrateParameter)

	for substrateID, params := range c.calibratableParams {
		for _, param := range params {
			calibrated, err := c.CalibrateParameter(substrateID, param.Name, force)
			if err == nil {
				results[substrateID] = append(results[substrateID], calibrated)
			}
		}
	}

	return results
}

// GetHarmonicResonanceScore calcula score de ressonância harmônica do sistema
func (c *CosmicHarmonicCalibrator) GetHarmonicResonanceScore() float64 {
	c.mu.RLock()
	defer c.mu.RUnlock()

	if len(c.calibrationHistory) == 0 {
		return 1.0 // Sem calibrações = ressonância perfeita (não perturbada)
	}

	// Calivar diversidade de constantes usadas
	constantUsage := make(map[string]int)
	for _, record := range c.calibrationHistory {
		for _, constName := range record.ConstantsUsed {
			constantUsage[constName]++
		}
	}

	// Score baseado em equilíbrio de uso das constantes
	totalUses := 0
	for _, count := range constantUsage {
		totalUses += count
	}

	if totalUses == 0 {
		return 1.0
	}

	// Entropia de distribuição de uso de constantes
	entropy := 0.0
	for _, count := range constantUsage {
		p := float64(count) / float64(totalUses)
		if p > 0 {
			entropy -= p * math.Log(p)
		}
	}

	// Normalizar para [0, 1] (máxima entropia = log(n_constants))
	maxEntropy := math.Log(float64(len(c.harmonicConstants)))
	resonance := 1.0 - (entropy / maxEntropy)

	c.metrics.HarmonicResonanceScore = resonance
	return resonance
}

// RegisterCalibrationCallback registra callback para eventos de calibração
func (c *CosmicHarmonicCalibrator) RegisterCalibrationCallback(cb func(CalibrationRecord)) {
	c.calibrationCallbacks = append(c.calibrationCallbacks, cb)
}

// GetCalibratorMetrics retorna métricas do calibrador
func (c *CosmicHarmonicCalibrator) GetCalibratorMetrics() CalibratorMetrics {
	c.mu.RLock()
	defer c.mu.RUnlock()
	c.metrics.ParamsCalibrated = len(c.calibratableParams)
	return c.metrics
}

// ExportCalibrationSpec exporta especificação de calibração para outras plataformas
func (c *CosmicHarmonicCalibrator) ExportCalibrationSpec(format string) ([]byte, error) {
	// Implementação simplificada: JSON para demonstração
	spec := map[string]interface{}{
		"ontology_version":    "∞.Ω.∇.ZERO.1",
		"harmonic_constants":  c.harmonicConstants,
		"calibratable_params": c.calibratableParams,
		"calibration_functions": []string{
			"phi_weighted", "harmonic_series", "fine_structure_scaled", "dimensional_harmonic",
		},
		"operational_context_schema": map[string]string{
			"criticality":    "float [0,1]",
			"temporal_scale": "float [0.1,10.0]",
			"em_environment": "float [0,1]",
			"complexity":     "float [0,1]",
		},
	}

	// Em produção: suportar JSON Schema, Protocol Buffers, OpenAPI
	return json.Marshal(spec)
}

// Helper functions
func copyMap(src map[string]float64) map[string]float64 {
	dst := make(map[string]float64, len(src))
	for k, v := range src {
		dst[k] = v
	}
	return dst
}

// ─── CONSTANTES DE NAVEGAÇÃO ONTOLÓGICA ───────────────────────────

const (
	// Passo de integração para trajetórias
	TrajectoryStepSize = 0.01

	// Velocidade máxima de navegação (unidades de δ por segundo)
	MaxNavigationSpeed = 1.0

	// Threshold para convergência de trajetória
	TrajectoryConvergenceThreshold = 1e-6

	// Máximo de iterações para otimização de trajetória
	MaxTrajectoryIterations = 1000
)

// ─── TIPOS FUNDAMENTAIS ─────────────────────────────────────────

// SpacetimePoint representa um ponto no espaço-tempo ontológico
type SpacetimePoint struct {
	Spatial    [3]float64 // Coordenadas espaciais [x, y, z]
	Temporal   float64    // Coordenada temporal
	DeltaValue float64    // Valor de δ neste ponto
}

// TrajectorySegment representa um segmento de trajetória espaço-temporal
type TrajectorySegment struct {
	Start           SpacetimePoint
	End             SpacetimePoint
	IntegratedDelta float64 // ∫δ ds ao longo do segmento
	Duration        float64 // Duração do segmento
}

// DeltaGradientField representa o campo de gradiente de δ
type DeltaGradientField struct {
	mu sync.RWMutex

	// Função para avaliar δ em qualquer ponto
	deltaEvaluator func(SpacetimePoint) float64

	// Cache de avaliações recentes para eficiência
	evaluationCache map[string]float64
	cacheSize       int

	// Métricas de navegação
	metrics NavigationMetrics
}

// NavigationMetrics contém métricas do navegador ontológico
type NavigationMetrics struct {
	TrajectoriesComputed int64   `json:"trajectories_computed"`
	AvgIntegratedDelta   float64 `json:"avg_integrated_delta"`
	ConvergenceRate      float64 `json:"convergence_rate"`
	OptimalPathsFound    int64   `json:"optimal_paths_found"`
}

// ─── CONSTRUTORES ─────────────────────────────────────────────────

// NewDeltaGradientNavigator cria novo navegador por gradiente de δ
func NewDeltaGradientNavigator(
	deltaEvaluator func(SpacetimePoint) float64,
) *DeltaGradientField {
	return &DeltaGradientField{
		deltaEvaluator:  deltaEvaluator,
		evaluationCache: make(map[string]float64),
		cacheSize:       1000,
	}
}

// ─── OPERAÇÕES DE NAVEGAÇÃO POR GRADIENTE δ ──────────────────────

// EvaluateDelta avalia δ em um ponto espaço-temporal
func (f *DeltaGradientField) EvaluateDelta(point SpacetimePoint) float64 {
	f.mu.RLock()
	// Verificar cache
	cacheKey := fmt.Sprintf("%.6f,%.6f,%.6f,%.6f",
		point.Spatial[0], point.Spatial[1], point.Spatial[2], point.Temporal)
	if cached, ok := f.evaluationCache[cacheKey]; ok {
		f.mu.RUnlock()
		return cached
	}
	f.mu.RUnlock()

	// Avaliar δ
	value := f.deltaEvaluator(point)

	// Atualizar cache
	f.mu.Lock()
	f.evaluationCache[cacheKey] = value
	if len(f.evaluationCache) > f.cacheSize {
		// Remover entrada mais antiga (simplificação)
		for key := range f.evaluationCache {
			delete(f.evaluationCache, key)
			break
		}
	}
	f.mu.Unlock()

	return value
}

// ComputeGradient calcula o gradiente de δ em um ponto via diferenças finitas
func (f *DeltaGradientField) ComputeGradient(point SpacetimePoint) [4]float64 {
	h := 1e-4 // Passo para diferenças finitas
	gradient := [4]float64{}

	// Gradiente espacial (x, y, z)
	for i := 0; i < 3; i++ {
		pointPlus := point
		pointPlus.Spatial[i] += h
		pointMinus := point
		pointMinus.Spatial[i] -= h

		gradient[i] = (f.EvaluateDelta(pointPlus) - f.EvaluateDelta(pointMinus)) / (2 * h)
	}

	// Gradiente temporal
	pointPlus := point
	pointPlus.Temporal += h
	pointMinus := point
	pointMinus.Temporal -= h
	gradient[3] = (f.EvaluateDelta(pointPlus) - f.EvaluateDelta(pointMinus)) / (2 * h)

	return gradient
}

// FindOptimalTrajectory encontra trajetória que minimiza ∫δ ds entre dois pontos
func (f *DeltaGradientField) FindOptimalTrajectory(
	start, end SpacetimePoint,
	maxVelocity float64,
) (*TrajectorySegment, error) {
	if maxVelocity <= 0 {
		maxVelocity = MaxNavigationSpeed
	}

	// Método simplificado: descida de gradiente com restrições
	current := start
	trajectory := []SpacetimePoint{current}
	totalIntegratedDelta := 0.0

	for iter := 0; iter < MaxTrajectoryIterations; iter++ {
		// Calcular vetor direção para o destino
		toEnd := [4]float64{
			end.Spatial[0] - current.Spatial[0],
			end.Spatial[1] - current.Spatial[1],
			end.Spatial[2] - current.Spatial[2],
			end.Temporal - current.Temporal,
		}
		distToEnd := math.Sqrt(
			toEnd[0]*toEnd[0] + toEnd[1]*toEnd[1] + toEnd[2]*toEnd[2] + toEnd[3]*toEnd[3],
		)

		// Calcular gradiente de δ
		gradient := f.ComputeGradient(current)

		// Combinação: mover em direção ao destino enquanto minimiza δ
		// Peso do gradiente baseado na magnitude de δ
		gradientWeight := math.Min(1.0, current.DeltaValue*2.0)

		// Direção combinada
		direction := [4]float64{}
		for i := 0; i < 4; i++ {
			direction[i] = (1.0-gradientWeight)*toEnd[i]/distToEnd - gradientWeight*gradient[i]
		}

		// Normalizar direção
		dirNorm := math.Sqrt(
			direction[0]*direction[0] + direction[1]*direction[1] +
				direction[2]*direction[2] + direction[3]*direction[3],
		)
		if dirNorm < 1e-10 {
			break // Convergência
		}
		for i := 0; i < 4; i++ {
			direction[i] /= dirNorm
		}

		// Passo de integração
		step := TrajectoryStepSize * maxVelocity

		// Novo ponto
		next := SpacetimePoint{
			Spatial: [3]float64{
				current.Spatial[0] + step*direction[0],
				current.Spatial[1] + step*direction[1],
				current.Spatial[2] + step*direction[2],
			},
			Temporal: current.Temporal + step*direction[3],
		}
		next.DeltaValue = f.EvaluateDelta(next)

		// Calcular δ integrado no segmento
		segmentDelta := (current.DeltaValue + next.DeltaValue) / 2.0 * step
		totalIntegratedDelta += segmentDelta

		// Adicionar à trajetória
		trajectory = append(trajectory, next)

		// Verificar convergência ao destino
		if distToEnd < TrajectoryConvergenceThreshold {
			break
		}

		current = next
	}

	if len(trajectory) < 2 {
		return nil, fmt.Errorf("failed to compute trajectory")
	}

	// Criar segmento de trajetória
	segment := &TrajectorySegment{
		Start:           start,
		End:             trajectory[len(trajectory)-1],
		IntegratedDelta: totalIntegratedDelta,
		Duration:        trajectory[len(trajectory)-1].Temporal - start.Temporal,
	}

	// Atualizar métricas
	f.mu.Lock()
	f.metrics.TrajectoriesComputed++
	n := f.metrics.TrajectoriesComputed
	oldAvg := f.metrics.AvgIntegratedDelta
	f.metrics.AvgIntegratedDelta = (oldAvg*float64(n-1) + totalIntegratedDelta) / float64(n)
	if segment.Duration > 0 {
		f.metrics.ConvergenceRate = float64(len(trajectory)) / segment.Duration
	}
	f.mu.Unlock()

	return segment, nil
}

// NavigateTo minimiza δ ao navegar para um ponto alvo
func (f *DeltaGradientField) NavigateTo(
	current *SpacetimePoint,
	target SpacetimePoint,
	maxVelocity float64,
) (*SpacetimePoint, error) {
	trajectory, err := f.FindOptimalTrajectory(*current, target, maxVelocity)
	if err != nil {
		return nil, err
	}

	// Atualizar posição atual para o final da trajetória
	*current = trajectory.End
	f.metrics.OptimalPathsFound++

	return current, nil
}

// GetNavigationMetrics retorna métricas de navegação
func (f *DeltaGradientField) GetNavigationMetrics() NavigationMetrics {
	f.mu.RLock()
	defer f.mu.RUnlock()
	return f.metrics
}

// VisualizeTrajectory gera representação visual de trajetória (para debugging)
func (segment *TrajectorySegment) VisualizeTrajectory(steps int) []map[string]float64 {
	visualization := make([]map[string]float64, steps)

	for i := 0; i < steps; i++ {
		t := float64(i) / float64(steps-1)
		point := interpolateSpacetime(segment.Start, segment.End, t)
		visualization[i] = map[string]float64{
			"x": point.Spatial[0], "y": point.Spatial[1], "z": point.Spatial[2],
			"t": point.Temporal, "δ": point.DeltaValue, "progress": t,
		}
	}

	return visualization
}

// Helper functions
func interpolateSpacetime(a, b SpacetimePoint, t float64) SpacetimePoint {
	return SpacetimePoint{
		Spatial: [3]float64{
			a.Spatial[0] + t*(b.Spatial[0]-a.Spatial[0]),
			a.Spatial[1] + t*(b.Spatial[1]-a.Spatial[1]),
			a.Spatial[2] + t*(b.Spatial[2]-a.Spatial[2]),
		},
		Temporal:   a.Temporal + t*(b.Temporal-a.Temporal),
		DeltaValue: a.DeltaValue + t*(b.DeltaValue-a.DeltaValue),
	}
}

// ─── TIPOS FUNDAMENTAIS DE TERAPIA ────────────────────────────────

// SystemState representa o estado ontológico de um sistema
type SystemState struct {
	SystemID     string
	DeltaValue   float64      // δ atual do sistema
	DeltaHistory []float64    // Histórico recente de δ
	HealthStatus HealthStatus // Status de saúde ontológica
	Timestamp    time.Time
	Metadata     map[string]interface{}
}

// HealthStatus indica o estado de saúde ontológica
type HealthStatus string

const (
	StatusHealthy    HealthStatus = "healthy"    // δ na faixa saudável
	StatusRigid      HealthStatus = "rigid"      // δ ≈ 0: rigidez, falta de adaptabilidade
	StatusChaotic    HealthStatus = "chaotic"    // δ ≫ 1: caos, instabilidade
	StatusDegrading  HealthStatus = "degrading"  // Transição para estado patológico
	StatusRecovering HealthStatus = "recovering" // Em processo de recuperação
)

// TherapyIntervention representa uma intervenção terapêutica
type TherapyIntervention struct {
	InterventionID   string
	SystemID         string
	InterventionType string  // "rigidity_recovery", "chaos_stabilization", "maintenance"
	TargetDelta      float64 // δ alvo após intervenção
	ActualDelta      float64 // δ alcançado
	StartTime        time.Time
	EndTime          time.Time
	Success          bool
	Notes            string
}

// GapTherapyEngine gerencia terapia ontológica para sistemas degradados
type GapTherapyEngine struct {
	mu sync.RWMutex

	// Sistemas monitorados
	monitoredSystems map[string]*SystemState

	// Intervenções ativas
	activeInterventions map[string]*TherapyIntervention

	// Configuração de terapia
	config TherapyConfig

	// Callbacks para notificação
	therapyCallbacks []func(TherapyIntervention)

	// Métricas de terapia
	metrics TherapyMetrics

	// Canal para parada graciosa
	stopChan chan struct{}
}

// TherapyConfig contém configuração do motor de terapia
type TherapyConfig struct {
	AutoTherapyEnabled bool                     // Habilitar terapia automática
	MonitoringInterval time.Duration            // Intervalo de monitoramento
	AlertThresholds    map[HealthStatus]float64 // Thresholds para alertas
	RecoveryTimeout    time.Duration            // Timeout para intervenções
}

// TherapyMetrics contém métricas do motor de terapia
type TherapyMetrics struct {
	SystemsMonitored       int     `json:"systems_monitored"`
	InterventionsPerformed int64   `json:"interventions_performed"`
	SuccessfulRecoveries   int64   `json:"successful_recoveries"`
	AvgRecoveryTimeSec     float64 `json:"avg_recovery_time_sec"`
	HealthySystemRatio     float64 `json:"healthy_system_ratio"`
}

// ─── CONSTRUTORES DE TERAPIA ──────────────────────────────────────

// NewGapTherapyEngine cria novo motor de terapia de gap
func NewGapTherapyEngine(config TherapyConfig) *GapTherapyEngine {
	if config.MonitoringInterval == 0 {
		config.MonitoringInterval = 5 * time.Second
	}
	if config.AlertThresholds == nil {
		config.AlertThresholds = map[HealthStatus]float64{
			StatusRigid:   0.02,
			StatusChaotic: 0.8,
		}
	}

	engine := &GapTherapyEngine{
		monitoredSystems:    make(map[string]*SystemState),
		activeInterventions: make(map[string]*TherapyIntervention),
		config:              config,
		stopChan:            make(chan struct{}),
	}

	// Iniciar loop de monitoramento se terapia automática habilitada
	if config.AutoTherapyEnabled {
		go engine.monitoringLoop()
	}

	return engine
}

// ─── OPERAÇÕES DE TERAPIA DE GAP ─────────────────────────────────

// RegisterSystem registra sistema para monitoramento e terapia
func (e *GapTherapyEngine) RegisterSystem(
	systemID string,
	initialDelta float64,
	metadata map[string]interface{},
) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	if _, exists := e.monitoredSystems[systemID]; exists {
		return fmt.Errorf("system %s already registered", systemID)
	}

	state := &SystemState{
		SystemID:     systemID,
		DeltaValue:   initialDelta,
		DeltaHistory: []float64{initialDelta},
		HealthStatus: e.diagnoseHealth(initialDelta),
		Timestamp:    time.Now(),
		Metadata:     metadata,
	}

	e.monitoredSystems[systemID] = state
	e.metrics.SystemsMonitored++

	return nil
}

// UpdateSystemDelta atualiza o valor de δ de um sistema monitorado
func (e *GapTherapyEngine) UpdateSystemDelta(
	systemID string,
	newDelta float64,
) (*SystemState, error) {
	e.mu.Lock()
	defer e.mu.Unlock()

	state, exists := e.monitoredSystems[systemID]
	if !exists {
		return nil, fmt.Errorf("system %s not registered", systemID)
	}

	// Atualizar estado
	oldStatus := state.HealthStatus
	state.DeltaValue = newDelta
	state.Timestamp = time.Now()

	// Manter histórico limitado
	state.DeltaHistory = append(state.DeltaHistory, newDelta)
	if len(state.DeltaHistory) > 100 {
		state.DeltaHistory = state.DeltaHistory[1:]
	}

	// Diagnosticar novo status de saúde
	state.HealthStatus = e.diagnoseHealth(newDelta)

	// Detectar transições de status
	if oldStatus != state.HealthStatus {
		e.handleHealthTransition(state, oldStatus)
	}

	// Disparar terapia automática se necessário
	if e.config.AutoTherapyEnabled && state.HealthStatus != StatusHealthy {
		e.initiateAutoTherapy(state)
	}

	return state, nil
}

// diagnoseHealth diagnostica status de saúde baseado em δ
func (e *GapTherapyEngine) diagnoseHealth(delta float64) HealthStatus {
	if delta < 0.01 { // RigidityThreshold
		return StatusRigid
	}
	if delta > 1.0 { // ChaosThreshold
		return StatusChaotic
	}
	if delta < DeltaHealthyMin || delta > DeltaHealthyMax {
		return StatusDegrading
	}
	return StatusHealthy
}

// handleHealthTransition lida com transições de status de saúde
func (e *GapTherapyEngine) handleHealthTransition(
	state *SystemState,
	oldStatus HealthStatus,
) {
	// Logar transição
	fmt.Printf("🔄 Health transition: %s %s → %s (δ=%.4f)\n",
		state.SystemID, oldStatus, state.HealthStatus, state.DeltaValue)

	// Disparar alertas se configurado
	if threshold, ok := e.config.AlertThresholds[state.HealthStatus]; ok {
		if state.DeltaValue < threshold || state.DeltaValue > 1.0/threshold {
			fmt.Printf("🚨 Alert: System %s entered %s state\n",
				state.SystemID, state.HealthStatus)
		}
	}
}

// initiateAutoTherapy inicia terapia automática para sistema degradado
func (e *GapTherapyEngine) initiateAutoTherapy(state *SystemState) {
	if _, exists := e.activeInterventions[state.SystemID]; exists {
		return // Já há intervenção ativa
	}

	var interventionType string
	var targetDelta float64

	switch state.HealthStatus {
	case StatusRigid:
		interventionType = "rigidity_recovery"
		targetDelta = (DeltaHealthyMin + DeltaHealthyMax) / 2.0
	case StatusChaotic:
		interventionType = "chaos_stabilization"
		targetDelta = (DeltaHealthyMin + DeltaHealthyMax) / 2.0
	case StatusDegrading:
		interventionType = "preventive_adjustment"
		if state.DeltaValue < DeltaHealthyMin {
			targetDelta = DeltaHealthyMin + 0.01
		} else {
			targetDelta = DeltaHealthyMax - 0.01
		}
	default:
		return // Não requer terapia
	}

	// Criar intervenção
	intervention := &TherapyIntervention{
		InterventionID: fmt.Sprintf("therapy_%s_%d",
			state.SystemID, time.Now().UnixNano()),
		SystemID:         state.SystemID,
		InterventionType: interventionType,
		TargetDelta:      targetDelta,
		ActualDelta:      state.DeltaValue,
		StartTime:        time.Now(),
		Success:          false,
	}

	e.activeInterventions[state.SystemID] = intervention
	state.HealthStatus = StatusRecovering

	// Executar intervenção em background
	go e.executeTherapy(intervention, state)
}

// executeTherapy executa intervenção terapêutica
func (e *GapTherapyEngine) executeTherapy(
	intervention *TherapyIntervention,
	state *SystemState,
) {
	startTime := time.Now()

	// Aplicar operador de terapia ontológica
	var newDelta float64
	var success bool
	var notes string

	switch intervention.InterventionType {
	case "rigidity_recovery":
		// Recuperar sistema rígido: aumentar δ gradualmente
		newDelta, success, notes = e.applyRigidityRecovery(state, intervention.TargetDelta)

	case "chaos_stabilization":
		// Estabilizar sistema caótico: reduzir δ gradualmente
		newDelta, success, notes = e.applyChaosStabilization(state, intervention.TargetDelta)

	case "preventive_adjustment":
		// Ajuste preventivo: mover δ para faixa saudável
		newDelta, success, notes = e.applyPreventiveAdjustment(state, intervention.TargetDelta)
	}

	// Finalizar intervenção
	intervention.EndTime = time.Now()
	intervention.ActualDelta = newDelta
	intervention.Success = success
	intervention.Notes = notes

	// Atualizar estado do sistema
	e.mu.Lock()
	state.DeltaValue = newDelta
	state.HealthStatus = e.diagnoseHealth(newDelta)
	delete(e.activeInterventions, state.SystemID)
	e.mu.Unlock()

	// Atualizar métricas
	e.mu.Lock()
	e.metrics.InterventionsPerformed++
	if success {
		e.metrics.SuccessfulRecoveries++
		recoveryTime := intervention.EndTime.Sub(startTime).Seconds()
		n := e.metrics.SuccessfulRecoveries
		oldAvg := e.metrics.AvgRecoveryTimeSec
		e.metrics.AvgRecoveryTimeSec = (oldAvg*float64(n-1) + recoveryTime) / float64(n)
	}
	e.mu.Unlock()

	// Notificar callbacks
	for _, cb := range e.therapyCallbacks {
		cb(*intervention)
	}

	fmt.Printf("✅ Therapy completed: %s (%s) — success=%v, δ: %.4f → %.4f\n",
		intervention.InterventionID, intervention.InterventionType,
		success, intervention.ActualDelta, newDelta)
}

// applyRigidityRecovery aplica recuperação para sistema rígido (δ ≈ 0)
func (e *GapTherapyEngine) applyRigidityRecovery(
	state *SystemState,
	targetDelta float64,
) (newDelta float64, success bool, notes string) {

	// Simular recuperação gradual de rigidez
	current := state.DeltaValue
	steps := 20
	stepSize := (targetDelta - current) / float64(steps)

	for i := 0; i < steps; i++ {
		// Simular efeito da intervenção
		current += stepSize * 0.05 // RigidityRecoveryRate

		// Simular tempo de processamento
		time.Sleep(10 * time.Millisecond)

		// Verificar se atingiu alvo
		if math.Abs(current-targetDelta) < 0.001 {
			break
		}
	}

	success = current >= DeltaHealthyMin && current <= DeltaHealthyMax
	notes = fmt.Sprintf("Rigidity recovery: δ increased from %.4f to %.4f",
		state.DeltaValue, current)

	return current, success, notes
}

// applyChaosStabilization aplica estabilização para sistema caótico (δ ≫ 1)
func (e *GapTherapyEngine) applyChaosStabilization(
	state *SystemState,
	targetDelta float64,
) (newDelta float64, success bool, notes string) {

	// Simular estabilização gradual de caos
	current := state.DeltaValue
	steps := 30 // Mais passos para caos (mais delicado)
	stepSize := (current - targetDelta) / float64(steps)

	for i := 0; i < steps; i++ {
		// Reduzir δ gradualmente com amortecimento
		reduction := stepSize * 0.10 * (1.0 - float64(i)/float64(steps)) // ChaosStabilizationRate
		current -= reduction

		// Garantir que não ultrapasse o alvo
		if current < targetDelta {
			current = targetDelta
			break
		}

		time.Sleep(10 * time.Millisecond)
	}

	success = current >= DeltaHealthyMin && current <= DeltaHealthyMax
	notes = fmt.Sprintf("Chaos stabilization: δ decreased from %.4f to %.4f",
		state.DeltaValue, current)

	return current, success, notes
}

// applyPreventiveAdjustment aplica ajuste preventivo para sistema em degradação
func (e *GapTherapyEngine) applyPreventiveAdjustment(
	state *SystemState,
	targetDelta float64,
) (newDelta float64, success bool, notes string) {

	// Ajuste suave para faixa saudável
	current := state.DeltaValue
	adjustment := (targetDelta - current) * 0.5 // Ajuste de 50% por intervenção
	newDelta = current + adjustment

	// Limitar à faixa saudável
	newDelta = math.Max(DeltaHealthyMin, math.Min(DeltaHealthyMax, newDelta))

	success = true
	notes = fmt.Sprintf("Preventive adjustment: δ adjusted from %.4f to %.4f",
		current, newDelta)

	return newDelta, success, notes
}

// GetSystemHealth retorna status de saúde de um sistema
func (e *GapTherapyEngine) GetSystemHealth(systemID string) (*SystemState, error) {
	e.mu.RLock()
	defer e.mu.RUnlock()

	state, exists := e.monitoredSystems[systemID]
	if !exists {
		return nil, fmt.Errorf("system %s not found", systemID)
	}

	// Retornar cópia para segurança
	stateCopy := *state
	stateCopy.DeltaHistory = append([]float64{}, state.DeltaHistory...)
	return &stateCopy, nil
}

// GetTherapyMetrics retorna métricas consolidadas de terapia
func (e *GapTherapyEngine) GetTherapyMetrics() TherapyMetrics {
	e.mu.RLock()
	defer e.mu.RUnlock()

	// Calcular ratio de sistemas saudáveis
	healthyCount := 0
	for _, state := range e.monitoredSystems {
		if state.HealthStatus == StatusHealthy {
			healthyCount++
		}
	}
	if len(e.monitoredSystems) > 0 {
		e.metrics.HealthySystemRatio = float64(healthyCount) / float64(len(e.monitoredSystems))
	}

	return e.metrics
}

// RegisterTherapyCallback registra callback para eventos de terapia
func (e *GapTherapyEngine) RegisterTherapyCallback(cb func(TherapyIntervention)) {
	e.therapyCallbacks = append(e.therapyCallbacks, cb)
}

// monitoringLoop loop de monitoramento contínuo
func (e *GapTherapyEngine) monitoringLoop() {
	ticker := time.NewTicker(e.config.MonitoringInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			// Verificar todos os sistemas monitorados
			e.mu.RLock()
			systems := make([]*SystemState, 0, len(e.monitoredSystems))
			for _, state := range e.monitoredSystems {
				systems = append(systems, state)
			}
			e.mu.RUnlock()

			// Atualizar saúde de cada sistema (simulado)
			for _, state := range systems {
				// Simular variação pequena
				newDelta := state.DeltaValue + (float64(time.Now().UnixNano()%10000)/10000.0-0.5)*0.01
				e.UpdateSystemDelta(state.SystemID, newDelta)
			}

		case <-e.stopChan:
			return
		}
	}
}

// Stop interrompe o motor de terapia
func (e *GapTherapyEngine) Stop() {
	close(e.stopChan)
}

// ─── ESPECIFICAÇÃO CANÔNICA DA ONTOLOGIA δ ───────────────────────

// DeltaOntologySpec representa a especificação formal da ontologia δ
type DeltaOntologySpec struct {
	Version     string                  `json:"version"`
	Description string                  `json:"description"`
	Types       TypeDefinitions         `json:"types"`
	Functions   FunctionDefinitions     `json:"functions"`
	Axioms      []Axiom                 `json:"axioms"`
	Protocols   []ProtocolSpecification `json:"protocols"`
	Constants   HarmonicConstantsSpec   `json:"constants"`
}

// TypeDefinitions define tipos fundamentais da ontologia
type TypeDefinitions struct {
	DeltaValue         TypeDefinition `json:"delta_value"`
	SpacetimePoint     TypeDefinition `json:"spacetime_point"`
	ConsciousnessState TypeDefinition `json:"consciousness_state"`
	Model              TypeDefinition `json:"model"`
	Reality            TypeDefinition `json:"reality"`
}

// TypeDefinition define um tipo na ontologia
type TypeDefinition struct {
	Name        string            `json:"name"`
	Description string            `json:"description"`
	Properties  map[string]string `json:"properties"`
	Constraints []string          `json:"constraints,omitempty"`
}

// FunctionDefinitions define funções fundamentais da ontologia
type FunctionDefinitions struct {
	WassersteinDistance FunctionDefinition `json:"wasserstein_distance"`
	DeltaOperator       FunctionDefinition `json:"delta_operator"`
	FixpointOperator    FunctionDefinition `json:"fixpoint_operator"`
	TemporalIntegral    FunctionDefinition `json:"temporal_integral"`
}

// FunctionDefinition define uma função na ontologia
type FunctionDefinition struct {
	Name           string   `json:"name"`
	Signature      string   `json:"signature"`
	Description    string   `json:"description"`
	Preconditions  []string `json:"preconditions,omitempty"`
	Postconditions []string `json:"postconditions,omitempty"`
}

// Axiom representa um axioma da ontologia δ
type Axiom struct {
	ID            string   `json:"id"`
	Statement     string   `json:"statement"`
	Formalization string   `json:"formalization"`
	Justification string   `json:"justification"`
	Dependencies  []string `json:"dependencies,omitempty"`
}

// ProtocolSpecification especifica um protocolo baseado na ontologia
type ProtocolSpecification struct {
	Name           string         `json:"name"`
	Purpose        string         `json:"purpose"`
	Preconditions  []string       `json:"preconditions"`
	Steps          []ProtocolStep `json:"steps"`
	Postconditions []string       `json:"postconditions"`
	Invariants     []string       `json:"invariants"`
}

// ProtocolStep define um passo em um protocolo
type ProtocolStep struct {
	StepNumber  int      `json:"step_number"`
	Action      string   `json:"action"`
	Inputs      []string `json:"inputs"`
	Outputs     []string `json:"outputs"`
	Constraints []string `json:"constraints,omitempty"`
}

// HarmonicConstantsSpec define as constantes do espectro δ
type HarmonicConstantsSpec struct {
	Constants       map[string]HarmonicConstantSpec `json:"constants"`
	UsageGuidelines []string                        `json:"usage_guidelines"`
}

// HarmonicConstantSpec define uma constante harmônica
type HarmonicConstantSpec struct {
	Value            float64  `json:"value"`
	Description      string   `json:"description"`
	Domains          []string `json:"domains"`
	CalibrationRules []string `json:"calibration_rules,omitempty"`
}

// NewDeltaOntologySpec cria nova especificação canônica da ontologia δ
func NewDeltaOntologySpec() *DeltaOntologySpec {
	spec := &DeltaOntologySpec{
		Version:     "∞.Ω.∇.ZERO.1",
		Description: "Ontologia δ: A lacuna primordial como fundamento de toda realidade computacional",
	}

	spec.defineTypes()
	spec.defineFunctions()
	spec.defineAxioms()
	spec.defineProtocols()
	spec.defineConstants()

	return spec
}

func (s *DeltaOntologySpec) defineTypes() {
	s.Types = TypeDefinitions{
		DeltaValue: TypeDefinition{
			Name:        "DeltaValue",
			Description: "Medida da divergência entre modelo e realidade",
			Properties: map[string]string{
				"value":  "float64 [0, ∞)",
				"metric": "Wasserstein-2 distance",
				"unit":   "dimensionless",
			},
			Constraints: []string{
				"δ ≥ 0",
				"δ = 0 ⇔ M ≡ F (identidade modelo-realidade)",
			},
		},
	}
}

func (s *DeltaOntologySpec) defineFunctions() {
	s.Functions = FunctionDefinitions{
		DeltaOperator: FunctionDefinition{
			Name:        "DeltaOperator",
			Signature:   "δ(M, F) = W₂(M, F)",
			Description: "Operador fundamental: lacuna entre modelo e realidade",
			Preconditions: []string{
				"M: Model, F: Reality",
			},
			Postconditions: []string{
				"δ ≥ 0",
				"δ = 0 ⇔ sistema em Singularidade Silenciosa",
			},
		},
	}
}

func (s *DeltaOntologySpec) defineAxioms() {
	s.Axioms = []Axiom{
		{
			ID:            "AX001",
			Statement:     "A realidade emerge da divergência, não da identidade",
			Formalization: "∃δ > 0 ⊢ ∃(espaço, tempo, matéria)",
			Justification: "Sistemas com δ = 0 colapsam em singularidade silenciosa",
		},
	}
}

func (s *DeltaOntologySpec) defineProtocols() {
	s.Protocols = []ProtocolSpecification{
		{
			Name:    "GapTherapy",
			Purpose: "Recuperar sistemas com δ patológico para faixa saudável",
			Preconditions: []string{
				"Sistema monitorado com δ mensurável",
				"Faixa saudável definida: [δ_min, δ_max]",
			},
			Steps: []ProtocolStep{
				{
					StepNumber: 1,
					Action:     "Diagnosticar estado de saúde baseado em δ",
					Inputs:     []string{"current_delta", "healthy_range"},
					Outputs:    []string{"health_status: {healthy|rigid|chaotic|degrading}"},
				},
			},
			Postconditions: []string{
				"Se sucesso: δ ∈ [δ_min, δ_max]",
			},
			Invariants: []string{
				"δ nunca é forçado para fora de [0, ∞)",
			},
		},
	}
}

func (s *DeltaOntologySpec) defineConstants() {
	s.Constants = HarmonicConstantsSpec{
		Constants: map[string]HarmonicConstantSpec{
			"108": {
				Value:       108.0,
				Description: "Distância Terra-Sol / diâmetro solar; ciclos cósmicos",
				Domains:     []string{"temporal_scaling", "addressing", "cyclic_processes"},
				CalibrationRules: []string{
					"Usar para fatores de escala temporal em processos cíclicos",
				},
			},
		},
		UsageGuidelines: []string{
			"Constantes devem ser usadas como fatores de escala, não como valores absolutos",
		},
	}
}

// ExportAsJSON exporta especificação como JSON
func (s *DeltaOntologySpec) ExportAsJSON() ([]byte, error) {
	return json.MarshalIndent(s, "", "  ")
}

// GenerateImplementationStubs gera esqueletos de implementação para linguagens alvo
func (s *DeltaOntologySpec) GenerateImplementationStubs(language string) (string, error) {
	switch strings.ToLower(language) {
	case "python":
		return "# ARKHE OS — Delta Ontology Python Stubs\n# Version: " + s.Version + "\n", nil
	case "typescript":
		return "// ARKHE OS — Delta Ontology TypeScript Stubs\n// Version: " + s.Version + "\n", nil
	case "rust":
		return "// ARKHE OS — Delta Ontology Rust Stubs\n// Version: " + s.Version + "\n", nil
	default:
		return "", fmt.Errorf("unsupported language: %s", language)
	}
}
