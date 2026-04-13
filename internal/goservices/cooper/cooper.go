package cooper

import (
	"context"
)

type Message struct {
	Type string
	Data []byte
}

type ClusterState struct {
	OrderParam float64
}

func NewCluster(nodes int) *ClusterState {
	return &ClusterState{OrderParam: 0.999}
}

func (cs *ClusterState) Broadcast(msg Message) {}

func (cs *ClusterState) WaitForAcks(ctx context.Context, msgType string) int {
	return 75
}

func (cs *ClusterState) CommitToLedger(eventType string, details string, sheet uint8) {}
