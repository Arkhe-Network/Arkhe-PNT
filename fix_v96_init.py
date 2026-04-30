import re

with open("scripts/arkhe_neuromorphic_embodied_v96.py", "r") as f:
    content = f.read()

# Fix 1: Properly initialize proprio_to_context in __init__
replacement_init = """        self.cerebellum = EventDrivenFiLM(
            input_dim=config.semantic_dim // 4,
            context_dim=config.context_dim,
            threshold=config.film_threshold,
            decay_rate=config.film_decay
        )

        self.proprio_to_context = nn.Linear(config.proprio_dim, config.context_dim)
"""
content = content.replace("        self.cerebellum = EventDrivenFiLM(\n            input_dim=config.semantic_dim // 4,\n            context_dim=config.context_dim,\n            threshold=config.film_threshold,\n            decay_rate=config.film_decay\n        )", replacement_init)

# Remove the dynamic initialization in forward pass
replacement_forward = """        # Adapt proprio_input to context_dim
        h_context = self.proprio_to_context(proprio_input)
"""
content = re.sub(r'# Adapt proprio_input to context_dim\s+if not hasattr\(self, "proprio_to_context"\):\s+self\.proprio_to_context = nn\.Linear\(proprio_input\.size\(-1\), self\.cerebellum\.gamma_proj\.in_features\)\.to\(proprio_input\.device\)\s+h_context = self\.proprio_to_context\(proprio_input\)', replacement_forward, content)


with open("scripts/arkhe_neuromorphic_embodied_v96.py", "w") as f:
    f.write(content)
