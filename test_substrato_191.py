import pytest
import asyncio
from unittest.mock import MagicMock

def test_decree(capsys):
    import substrato_191_quantum_fiber
    substrato_191_quantum_fiber.decree()
    captured = capsys.readouterr()
    assert "SUBSTRATO_191: QUANTUM_FIBER_OPTIMIZATION" in captured.out
    assert "EPR Clock Sync:" in captured.out
    assert "CANONICAL SEAL: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0" in captured.out

def test_optimize_fiber_span():
    import substrato_191_quantum_fiber
    result = asyncio.run(substrato_191_quantum_fiber.optimize_fiber_span("SPAN-TEST"))

    assert result["span_id"] == "SPAN-TEST"
    assert "new_osnr_target" in result
    assert "fec_scheme" in result
    assert "clock_offset_correction_ps" in result
    assert "dithering_amplitude" in result
