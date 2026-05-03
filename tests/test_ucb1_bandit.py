import pytest
from core.hardware.ucb1_bandit import UCB1KernelBandit

def test_ucb1_bandit_initialization():
    bandit = UCB1KernelBandit(kernel_ids=["A", "B", "C"])
    assert len(bandit.arms) == 3
    assert bandit.total_pulls == 0

def test_ucb1_bandit_exploration():
    bandit = UCB1KernelBandit(kernel_ids=["A", "B", "C"])
    # First 3 selections should pull each arm once
    selections = set()
    for _ in range(3):
        kid = bandit.select_kernel()
        selections.add(kid)
        bandit.update(kid, 1.0)
    assert selections == {"A", "B", "C"}
    assert bandit.total_pulls == 3

def test_ucb1_bandit_exploitation():
    bandit = UCB1KernelBandit(kernel_ids=["A", "B", "C"])
    for kid in ["A", "B", "C"]:
        bandit.select_kernel()
        if kid == "A":
            bandit.update(kid, 10.0) # High reward
        else:
            bandit.update(kid, 1.0)  # Low reward

    # Next selection should heavily favor A because of high reward
    assert bandit.select_kernel() == "A"
