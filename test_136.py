import pytest
from fastapi.testclient import TestClient
from arkhe_os.molecular_workshop.oracle import MolecularPublicOracle, MolecularSceneSetter, LiquidCrystalPredictor, MolecularCurator, CoCoGraphInterface
from arkhe_os.api.oracle_api import app

def test_scene_setter():
    setter = MolecularSceneSetter()
    scene = setter.set_scene("cristal líquido discótico com Tclear > 450")
    assert 'c1ccc2c(c1)ccc3ccccc23' in scene.required_substructures
    assert 'c1ccc2c(c1)cc3c4c2cccc4ccc5c3cccc5' in scene.required_substructures
    assert 'Tclear' in scene.target_properties
    assert scene.target_properties['Tclear'][0] == 450.0

def test_oracle_population():
    oracle = MolecularPublicOracle(db_path=":memory:")
    oracle.populate_from_cocograph(n_total=10, batch_size=10)

    # After population, let's test querying
    res = oracle.natural_language_query("Tclear > 400")
    assert isinstance(res, list)

def test_oracle_api():
    client = TestClient(app)
    # mock oracle for test
    app.dependency_overrides = {}
    response = client.get("/query", params={"prop": "tclear", "low": 400, "high": 500, "limit": 10})
    assert response.status_code == 200
    assert "results" in response.json()

    response = client.get("/nl_query", params={"thought": "Tclear > 400"})
    assert response.status_code == 200
    assert "results" in response.json()
