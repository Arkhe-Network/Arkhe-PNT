package lshtree

import (
	"bytes"
)

type LSHFunc func([]byte) []byte

type Node struct {
	Hash  []byte
	Left  *Node
	Right *Node
	Data  []byte // only for leaves
}

func NewLSHTree(data [][]byte, lsh LSHFunc) *Node {
	if len(data) == 0 {
		return nil
	}
	if len(data) == 1 {
		return &Node{Hash: lsh(data[0]), Data: data[0]}
	}
	mid := len(data) / 2
	left := NewLSHTree(data[:mid], lsh)
	right := NewLSHTree(data[mid:], lsh)
	combined := append(left.Hash, right.Hash...)
	hash := lsh(combined)
	return &Node{Hash: hash, Left: left, Right: right}
}

// Diff returns the differing bits between two LSH trees (for verification).
func Diff(a, b *Node) []byte {
	if a == nil && b == nil {
		return nil
	}
	if a == nil || b == nil {
		// One side missing: send full hash of the existing side
		if a != nil {
			return a.Hash
		}
		return b.Hash
	}
	if bytes.Equal(a.Hash, b.Hash) {
		return nil
	}
	// Otherwise, recursively diff children
	leftDiff := Diff(a.Left, b.Left)
	rightDiff := Diff(a.Right, b.Right)
	return append(leftDiff, rightDiff...)
}
