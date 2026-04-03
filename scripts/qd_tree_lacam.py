import heapq
import random
import math
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional

@dataclass(frozen=True, order=True)
class QDState:
    node_id: str
    phase: float = 0.0  # [0, 2pi)
    t2_star: float = 0.0 # [0, 100] us
    latency: float = 0.0 # [0, 500] ms
    stake: float = 0.0
    reputation: float = 0.0

    def __post_init__(self):
        object.__setattr__(self, 'phase', self.phase % (2 * math.pi))

@dataclass
class Action:
    name: str
    cost: float
    duration: float

ACTIONS = {
    "STAY": Action("STAY", 0.0, 0.0),
    "ALIGN": Action("ALIGN", 10.0, 50.0), # Modula fase
    "HANDSHAKE": Action("HANDSHAKE", 20.0, 50.0),
    "TELEPORT": Action("TELEPORT", 100.0, 100.0)
}

class SearchNode:
    def __init__(self, states: List[QDState], cost: float = 0.0, parent: 'SearchNode' = None, action_taken: str = None):
        self.states = tuple(states)
        self.cost = cost
        self.parent = parent
        self.action_taken = action_taken
        self.heuristic = self._calculate_heuristic()

    def _calculate_heuristic(self):
        # Estimated cost to align phases
        h = 0.0
        phases = [s.phase for s in self.states]
        # Coherence goal R(t) > 0.8
        r_t = abs(sum(complex(math.cos(p), math.sin(p)) for p in phases)) / len(phases)
        if r_t < 0.8:
            h += (0.8 - r_t) * 100.0
        return h

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

def transition(states: Tuple[QDState], action_set: Dict[str, str]) -> List[QDState]:
    new_states = []
    for s in states:
        action_name = action_set.get(s.node_id, "STAY")

        # Simple dynamics
        new_phase = (s.phase + 0.1) % (2 * math.pi)
        new_t2 = max(0, s.t2_star - 0.001)
        new_lat = s.latency + random.uniform(-1, 1)

        if action_name == "ALIGN":
            # Shift phase towards zero for simplicity in simulation
            target = 0.0
            diff = (target - new_phase + math.pi) % (2 * math.pi) - math.pi
            new_phase = (new_phase + diff * 0.5) % (2 * math.pi)
            new_states.append(QDState(s.node_id, new_phase, new_t2, new_lat, s.stake, s.reputation + 1.0))
        elif action_name == "HANDSHAKE":
            new_states.append(QDState(s.node_id, new_phase, new_t2, new_lat, s.stake, s.reputation + 2.0))
        elif action_name == "TELEPORT":
            new_states.append(QDState(s.node_id, new_phase, new_t2 - 2.0, new_lat, s.stake, s.reputation + 10.0))
        else:
            new_states.append(QDState(s.node_id, new_phase, new_t2, new_lat, s.stake, s.reputation))

    return new_states

def tree_lacam_qd(initial_states: List[QDState], goal_threshold: float = 0.8):
    print(f"🜏 [Archimedes] Iniciando Tree-LaCAM para {len(initial_states)} nós QD...")

    root = SearchNode(initial_states)
    queue = [root]
    visited = set()

    iterations = 0

    while queue and iterations < 5000:
        iterations += 1
        node = heapq.heappop(queue)

        r_t = abs(sum(complex(math.cos(p), math.sin(p)) for p in [s.phase for s in node.states])) / len(node.states)

        if r_t >= goal_threshold:
            print(f"✓ [Archimedes] Meta alcançada em {iterations} iterações. R(t)={r_t:.4f}")
            return node, r_t

        state_signature = tuple((s.node_id, round(s.phase, 1)) for s in node.states)
        if state_signature in visited:
            continue
        visited.add(state_signature)

        for i, s in enumerate(node.states):
            for act_name, act in ACTIONS.items():
                if act_name == "STAY" and i > 0: continue

                action_set = {s.node_id: act_name}
                new_states = transition(node.states, action_set)
                child = SearchNode(new_states, node.cost + act.cost, node, f"{s.node_id}:{act_name}")
                heapq.heappush(queue, child)

    print("✗ [Archimedes] Falha ao encontrar plano ótimo.")
    return None, 0.0

if __name__ == "__main__":
    init_states = [
        QDState("QD-01", phase=0.0, t2_star=55.0, latency=20.0, stake=100.0, reputation=900.0),
        QDState("QD-02", phase=math.pi, t2_star=48.0, latency=25.0, stake=120.0, reputation=850.0),
        QDState("QD-03", phase=math.pi/2, t2_star=42.0, latency=40.0, stake=80.0, reputation=700.0)
    ]

    plan_node, final_r = tree_lacam_qd(init_states)

    if plan_node:
        path = []
        curr = plan_node
        while curr:
            if curr.action_taken: path.append(curr.action_taken)
            curr = curr.parent
        print(f"Plano de Handover Concreto: {' -> '.join(reversed(path))}")
        print(f"Custo Total: {plan_node.cost}")
        print(f"Coerência Final: {final_r:.4f}")
