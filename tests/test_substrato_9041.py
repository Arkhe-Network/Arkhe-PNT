import pytest
import asyncio
from arkhe_moire.materials_2d_db import MATERIALS_2D_CATALOG, MaterialClass
from arkhe_moire.qnc_optimizer import QNCCriticalAngleOptimizer
from arkhe_moire.bridge import MoireArkheBridge

def test_materials_catalog():
    assert "CrI3" in MATERIALS_2D_CATALOG
    assert "BaTiO3_2d" in MATERIALS_2D_CATALOG
    assert MATERIALS_2D_CATALOG["CrI3"].material_class == MaterialClass.MAGNETIC_TMD

def test_qnc_optimizer():
    optimizer = QNCCriticalAngleOptimizer()
    optimizer.train(MATERIALS_2D_CATALOG)
    assert optimizer._trained is True

    mat = MATERIALS_2D_CATALOG["CrI3"]
    predicted_angle = optimizer.predict_optimal_angle(mat, temperature_k=4.2)
    assert predicted_angle >= 0.0

    optimal_angle, max_phi = optimizer.optimize_via_gradient_ascent(mat, initial_guess=1.0)
    assert optimal_angle >= 0.0
    assert max_phi > 0.0

@pytest.mark.asyncio
async def test_moire_bridge():
    bridge = MoireArkheBridge()
    result = await bridge.run_qnc_optimization("MoSSe", temperature_k=4.2)
    assert result["material"] == "Molybdenum Sulfide Selenide"
    assert result["method"] == "qnc_prediction + gradient_ascent"
    assert result["optimal_angle"] >= 0.0
