# ucb1_bandit.py
# =============================================================================
# Substrate 123.1 — UCB1 Bandit for Kernel Zoo Selection
#
# The fast A∘P loop selects from pre-verified kernel variants using the
# UCB1 algorithm to balance exploration and exploitation based on
# performance feedback.
# =============================================================================

import math
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class KernelArm:
    """Represents a kernel variant in the zoo."""
    id: str
    name: str
    pulls: int = 0
    total_reward: float = 0.0

class UCB1KernelBandit:
    """
    UCB1 Multi-Armed Bandit for selecting the optimal kernel variant.

    The reward function should be designed such that higher values are better
    (e.g., lower latency, lower power, mercy gap preserved).
    """

    def __init__(self, kernel_ids: List[str], exploration_constant: float = math.sqrt(2)):
        self.arms = {kid: KernelArm(id=kid, name=kid) for kid in kernel_ids}
        self.exploration_constant = exploration_constant
        self.total_pulls = 0

    def select_kernel(self) -> str:
        """
        Selects the next kernel to execute based on UCB1.
        """
        # 1. Initialize: pull each arm once if unpulled
        for arm in self.arms.values():
            if arm.pulls == 0:
                return arm.id

        # 2. Compute UCB1 value for each arm
        best_arm = None
        best_ucb = -float('inf')

        for arm in self.arms.values():
            # Average reward (exploitation)
            average_reward = arm.total_reward / arm.pulls

            # Confidence bound (exploration)
            confidence_bound = self.exploration_constant * math.sqrt(
                math.log(self.total_pulls) / arm.pulls
            )

            ucb_value = average_reward + confidence_bound

            if ucb_value > best_ucb:
                best_ucb = ucb_value
                best_arm = arm.id

        return best_arm

    def update(self, kernel_id: str, reward: float):
        """
        Updates the statistics for a kernel arm after execution.
        """
        if kernel_id not in self.arms:
            raise ValueError(f"Unknown kernel ID: {kernel_id}")

        arm = self.arms[kernel_id]
        arm.pulls += 1
        arm.total_reward += reward
        self.total_pulls += 1

    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Returns the current statistics for all arms."""
        stats = {}
        for kid, arm in self.arms.items():
            avg_reward = arm.total_reward / arm.pulls if arm.pulls > 0 else 0.0
            stats[kid] = {
                "pulls": arm.pulls,
                "average_reward": avg_reward,
                "total_reward": arm.total_reward
            }
        return stats
