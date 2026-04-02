import json
import re
from typing import List, Dict, Tuple

class SemanticRouter:
    def __init__(self, legends_path: str):
        with open(legends_path) as f:
            self.legends = json.load(f)["assets"]
        self.intent_map = {
            "stability": ["GROUND", "MATTER"],
            "sovereignty": ["ANCHOR", "SHADOW"],
            "speculation": ["CHAOS"],
            "utility": ["STRUCTURE", "CONNECTOR"],
        }

    def parse_intent(self, text: str) -> Tuple[str, float]:
        """Retorna (intent, confiança)."""
        text_lower = text.lower()
        if re.search(r"estabil|segur|safe|ground", text_lower):
            return ("stability", 0.9)
        if re.search(r"soberan|privac|shadow|anchor", text_lower):
            return ("sovereignty", 0.9)
        if re.search(r"especul|comedy|troll|chaos|dog|pepe", text_lower):
            return ("speculation", 0.9)
        if re.search(r"util|program|scale|connect|link", text_lower):
            return ("utility", 0.9)
        return ("utility", 0.5)  # fallback

    def allocate(self, intent: str, amount_usd: float) -> List[Dict[str, float]]:
        """Retorna lista de alocações {symbol: percentual}."""
        allowed_archetypes = self.intent_map.get(intent, ["STRUCTURE"])
        candidates = [a for a in self.legends if a["archetype"] in allowed_archetypes]
        if not candidates:
            candidates = self.legends
        # distribuição igualitária (exemplo)
        per = 1.0 / len(candidates)
        return [{c["symbol"]: per} for c in candidates]

    def process(self, user_input: str, amount_usd: float) -> List[Dict[str, float]]:
        intent, _ = self.parse_intent(user_input)
        return self.allocate(intent, amount_usd)
