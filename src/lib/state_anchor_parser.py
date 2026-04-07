import re
import os

class StateAnchorParser:
    """
    Bridges MEMORY.md, DREAMS.md, and SOUL.md with the Lean 4 formalization.
    """
    def __init__(self, memory_path="MEMORY.md", dreams_path="DREAMS.md", soul_path="SOUL.md"):
        self.memory_path = memory_path
        self.dreams_path = dreams_path
        self.soul_path = soul_path

    def parse_current_identity(self):
        """Extracts current lambda and block height from MEMORY.md."""
        if not os.path.exists(self.memory_path):
            return None

        with open(self.memory_path, 'r') as f:
            content = f.read()

        lambda_match = re.search(r"λ₂\D+([\d.]+)", content)
        block_match = re.search(r"Block\D+([\d.]+)", content)

        block_val = 0
        if block_match:
            block_str = block_match.group(1).replace('.', '')
            block_val = int(block_str)

        return {
            "lambda": float(lambda_match.group(1)) if lambda_match else 0.0,
            "block": block_val
        }

    def parse_agent_soul(self, agent_id):
        """Parses an agent's SOUL.md to extract mission and minimal lambda."""
        # For simplicity, we assume one SOUL.md per agent for now
        if not os.path.exists(self.soul_path):
            return None

        with open(self.soul_path, 'r') as f:
            content = f.read()

        # Extract mission and coherence threshold
        mission_match = re.search(r"## Miss\u00e3o\n(.*)", content)
        lambda_match = re.search(r"## Coer\u00eancia M\u00ednima\n([\d.]+)", content)

        return {
            "agent_id": agent_id,
            "mission": mission_match.group(1).strip() if mission_match else "",
            "min_lambda": float(lambda_match.group(1)) if lambda_match else 0.85
        }
