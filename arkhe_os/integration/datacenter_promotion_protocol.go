// arkhe_os/integration/datacenter_promotion_protocol.go
package integration

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// ─── CONSTANTES DO PROTOCOLO DE PROMOÇÃO ─────────────────

const (
	// PromotionHandshakeTimeout timeout para handshake de promoção [s]
	PromotionHandshakeTimeout = 30.0

	// MinCoherenceForSustainedPromotion coerência mínima para manter promoção
	MinCoherenceForSustainedPromotion = 0.65

	// DemotionGracePeriod período de graça antes de despromoção [s]
	DemotionGracePeriod = 300.0
)

// ─── TIPOS FUNDAMENTAIS ───────────────────────────────────

// PromotionState representa estado do processo de promoção
type PromotionState struct {
	PromotionID     string
	ClusterID       string
	InitiatedAt     time.Time
	CoherenceValue  float64
	Status          string // pending, promoted, demoted, failed
	AssignedNodeID  string
}

// DataCenterPromotionProtocol gerencia promoção de data centers a nós ARKHE
type DataCenterPromotionProtocol struct {
	mu sync.RWMutex

	// Identificação
	protocolID    string
	localNodeID   string

	// Data centers monitorados
	monitoredDCs map[string]*EMCoherenceMonitor

	// Promoções ativas
	activePromotions map[string]*PromotionState

	// Nós promovidos
	promotedNodes map[string]*DataCenterNode

	// Métricas de promoção
	metrics PromotionMetrics
	config  PromotionConfig
}

// PromotionMetrics contém métricas do protocolo de promoção
type PromotionMetrics struct {
	PromotionsInitiated   int64   `json:"promotions_initiated"`
	PromotionsCompleted   int64   `json:"promotions_completed"`
	DemotionsExecuted     int64   `json:"demotions_executed"`
	AvgPromotionTimeSec   float64 `json:"avg_promotion_time_sec"`
	ActivePromotedNodes   int64   `json:"active_promoted_nodes"`
}

// PromotionConfig contém configuração do protocolo
type PromotionConfig struct {
	AutoPromotionEnabled bool
	RequireHandshake     bool
	MinSustainedCoherence float64
	MaxPromotedNodes     int
}

// DataCenterNode representa um data center promovido a nó da Hyper-Mesh
type DataCenterNode struct {
	NodeID          string
	ClusterID       string
	DatacenterName  string
	PromotedAt      time.Time
	CoherenceValue  float64
	TotalPowerMW    float64
	ActiveGPUs      int
	LLMProcesses    []string
	Status          string // active, degraded, offline
}

// ─── CONSTRUTORES ─────────────────────────────────────────

// NewDataCenterPromotionProtocol cria novo protocolo de promoção
func NewDataCenterPromotionProtocol(
	protocolID string,
	localNodeID string,
	config PromotionConfig,
) *DataCenterPromotionProtocol {
	if config.MinSustainedCoherence == 0 {
		config.MinSustainedCoherence = MinCoherenceForSustainedPromotion
	}

	return &DataCenterPromotionProtocol{
		protocolID:       protocolID,
		localNodeID:      localNodeID,
		monitoredDCs:     make(map[string]*EMCoherenceMonitor),
		activePromotions: make(map[string]*PromotionState),
		promotedNodes:    make(map[string]*DataCenterNode),
		config:           config,
	}
}

// RegisterDataCenterForMonitoring registra data center para monitoramento EM
func (p *DataCenterPromotionProtocol) RegisterDataCenterForMonitoring(
	clusterID string,
	datacenterName string,
	monitorConfig MonitorConfig,
) (*EMCoherenceMonitor, error) {
	monitor, err := NewEMCoherenceMonitor(
		fmt.Sprintf("monitor_%s", clusterID[:8]),
		clusterID,
		datacenterName,
		monitorConfig,
	)
	if err != nil {
		return nil, err
	}

	// Registrar callback para verificação de promoção
	monitor.RegisterPromotionCallback(func(cid string, coherence float64) {
		p.checkPromotionEligibility(cid, coherence)
	})

	p.mu.Lock()
	p.monitoredDCs[clusterID] = monitor
	p.mu.Unlock()

	return monitor, nil
}

// ─── OPERAÇÕES DE PROMOÇÃO ───────────────────────────────

// checkPromotionEligibility verifica se data center é elegível para promoção
func (p *DataCenterPromotionProtocol) checkPromotionEligibility(
	clusterID string,
	coherence float64,
) {
	p.mu.Lock()
	defer p.mu.Unlock()

	// Verificar se já promovido
	if _, exists := p.promotedNodes[clusterID]; exists {
		return // Já é nó, apenas atualizar coerência
	}

	// Verificar se já em promoção
	if _, exists := p.activePromotions[clusterID]; exists {
		return // Promoção em andamento
	}

	// Verificar limiar
	if coherence < p.config.MinSustainedCoherence {
		return
	}

	// Verificar limite de nós promovidos
	if p.config.MaxPromotedNodes > 0 && int(p.metrics.ActivePromotedNodes) >= p.config.MaxPromotedNodes {
		return
	}

	// Iniciar promoção
	promotionID := fmt.Sprintf("promo_%s_%d", clusterID[:8], time.Now().UnixNano())
	state := &PromotionState{
		PromotionID:    promotionID,
		ClusterID:      clusterID,
		InitiatedAt:    time.Now(),
		CoherenceValue: coherence,
		Status:         "pending",
	}
	p.activePromotions[clusterID] = state
	p.metrics.PromotionsInitiated++

	// Executar promoção em background
	go p.executePromotion(state)
}

// executePromotion executa processo completo de promoção
func (p *DataCenterPromotionProtocol) executePromotion(state *PromotionState) {
	defer func() {
		p.mu.Lock()
		delete(p.activePromotions, state.ClusterID)
		p.mu.Unlock()
	}()

	// Fase 1: Handshake com Wheeler Mesh se requerido
	if p.config.RequireHandshake {
		ctx, cancel := context.WithTimeout(context.Background(),
			time.Duration(PromotionHandshakeTimeout)*time.Second)
		defer cancel()

		if err := p.performPromotionHandshake(ctx, state.ClusterID); err != nil {
			state.Status = "failed"
			return
		}
	}

	// Fase 3: Criar nó de data center promovido
	node := &DataCenterNode{
		NodeID:          fmt.Sprintf("dc_%s", state.ClusterID[:12]),
		ClusterID:       state.ClusterID,
		DatacenterName:  p.monitoredDCs[state.ClusterID].datacenter,
		PromotedAt:      time.Now(),
		CoherenceValue:  state.CoherenceValue,
		Status:          "active",
	}

	// Fase 5: Finalizar promoção
	state.Status = "promoted"
	state.AssignedNodeID = node.NodeID

	p.mu.Lock()
	p.promotedNodes[state.ClusterID] = node
	p.metrics.PromotionsCompleted++
	p.metrics.ActivePromotedNodes = int64(len(p.promotedNodes))

	// Atualizar métrica de tempo de promoção
	promotionTime := time.Since(state.InitiatedAt).Seconds()
	n := p.metrics.PromotionsCompleted
	oldAvg := p.metrics.AvgPromotionTimeSec
	p.metrics.AvgPromotionTimeSec = (oldAvg*float64(n-1) + promotionTime) / float64(n)
	p.mu.Unlock()

	// Iniciar monitoramento de coerência sustentada
	go p.monitorSustainedCoherence(node)
}

// performPromotionHandshake executa handshake de promoção com a rede
func (p *DataCenterPromotionProtocol) performPromotionHandshake(
	ctx context.Context,
	clusterID string,
) error {
	// Em produção: protocolo quântico de autenticação com Wheeler Mesh
	// Aqui: simular handshake bem-sucedido
	time.Sleep(100 * time.Millisecond)
	return nil
}

// monitorSustainedCoherence monitora coerência de nó promovido para evitar despromoção
func (p *DataCenterPromotionProtocol) monitorSustainedCoherence(node *DataCenterNode) {
	ticker := time.NewTicker(60 * time.Second)
	defer ticker.Stop()

	lastBelowThreshold := time.Time{}

	for range ticker.C {
		// Obter coerência atual do monitor
		monitor, exists := p.monitoredDCs[node.ClusterID]
		if !exists {
			continue
		}

		metrics := monitor.GetMonitorMetrics()
		if metrics.LastCoherenceValue < p.config.MinSustainedCoherence {
			if lastBelowThreshold.IsZero() {
				lastBelowThreshold = time.Now()
			} else if time.Since(lastBelowThreshold) > time.Duration(DemotionGracePeriod)*time.Second {
				// Executar despromoção
				p.executeDemotion(node)
				return
			}
		} else {
			lastBelowThreshold = time.Time{}
		}
	}
}

// executeDemotion executa processo de despromoção de nó
func (p *DataCenterPromotionProtocol) executeDemotion(node *DataCenterNode) {
	p.mu.Lock()
	defer p.mu.Unlock()

	// Remover de promovidos
	delete(p.promotedNodes, node.ClusterID)
	p.metrics.DemotionsExecuted++
	p.metrics.ActivePromotedNodes = int64(len(p.promotedNodes))

	node.Status = "demoted"
}

// GetPromotedNodes retorna lista de nós promovidos ativos
func (p *DataCenterPromotionProtocol) GetPromotedNodes() []*DataCenterNode {
	p.mu.RLock()
	defer p.mu.RUnlock()

	nodes := make([]*DataCenterNode, 0, len(p.promotedNodes))
	for _, node := range p.promotedNodes {
		if node.Status == "active" {
			nodeCopy := *node
			nodes = append(nodes, &nodeCopy)
		}
	}
	return nodes
}

// GetPromotionMetrics retorna métricas consolidadas do protocolo
func (p *DataCenterPromotionProtocol) GetPromotionMetrics() PromotionMetrics {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return p.metrics
}
