with open("substrato_unbuildable.py", "r") as f:
    text = f.read()

# Make it use a real script representation to prevent infinite nesting indent bugs
import ast

def fix_ast():
    pass
