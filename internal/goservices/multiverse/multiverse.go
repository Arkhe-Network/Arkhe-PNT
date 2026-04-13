package multiverse

import (
	"context"
)

type TeleportRequest struct {
	SourceSheet int32
	DestSheet   int32
	QubitIndex  int32
	Hardware    string
}

type TeleportResult struct {
	Fidelity float64
	Latency  int64
}

type SheetManager struct {
	Count int
}

func NewSheetManager(count int) *SheetManager {
	return &SheetManager{Count: count}
}

func (sm *SheetManager) LockSheets(src, dest uint8) {}
func (sm *SheetManager) UnlockSheets(src, dest uint8) {}
func (sm *SheetManager) StatusHandler(c any) {}

type ZigVaultClient struct {
	Addr string
}

func NewZigVaultClient(addr string) *ZigVaultClient {
	return &ZigVaultClient{Addr: addr}
}

func (zvc *ZigVaultClient) Teleport(ctx context.Context, req *TeleportRequest) (*TeleportResult, error) {
	return &TeleportResult{Fidelity: 0.9843, Latency: 142}, nil
}
