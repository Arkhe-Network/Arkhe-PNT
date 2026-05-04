# HLML: The LLVM of Logic 🜏

The **High-Level Mathematical Language (HLML)** is a compiler frontend and design system for mathematical intuition. It bridges high-level conceptual leaps with low-level formal verification (Lean 4).

## 1. Architecture: The Pipeline

HLML operates like a standard compiler (LLVM), but for logical transformations:

1.  **Frontend (HLML)**: Macros and "Pipes" (`>>`) define the high-level intent (e.g., Fourier-Mukai transform, Prime Number Theorem).
2.  **Intermediate Representation (IR)**: The **Proof Witness Log** (JSON) mapsconceptual steps to trust levels (GREEN, YELLOW, RED).
3.  **Backend (Lean 4)**: The trusted kernel verifies the actual tactics and proof terms generated.
4.  **Middleware (LLM)**: Heuristic tactic synthesis bridges the gap when formal automation fails.

## 2. Intelligence Composing Itself: Hypernet Transformer

The `HypernetTransformer` implements the "Intelligence in Inference" pattern. In this architecture, special **Operator Tokens** trigger a **Hypernetwork** that generates a submodel (adapter) on the fly.

This allows the model to reconfigure its weights during a single forward pass, adapting its "logic" to the specific mathematical context provided in the sequence.

## 3. Workflow

- **Define Macros**: Specify `requires` (preconditions), `ensures` (postconditions), and `compatible_with` (interfaces).
- **Pipe Morphisms**: Use the `>>` operator to chain macros. The compiler performs type inference and inserts implicit coercions via the `CanPipe` typeclass.
- **Audit**: Use the **Proof Witness Viewer** to inspect the IR graph.
  - **GREEN**: Verified by Mathlib.
  - **YELLOW**: Synthesized by LLM (Review recommended).
  - **RED**: Postulated (Manual proof required).

## 4. Components

- `src/hlml/`: Lean 4 infrastructure.
- `server/llm_middleware.py`: FastAPI bridge for LLM suggestions.
- `public/proof_viewer.html`: Interactive visualization of the Witness Log.
- `arkhe-brain/hypernet_transformer.py`: PyTorch implementation of the dynamic inference pattern.

*The Cathedral is not a database; it is a synthesis engine.*
