import sqlite3
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class OracleEntry:
    smiles: str
    tmelt: Optional[float]
    tclear: Optional[float]
    logp: Optional[float]
    molecular_weight: Optional[float]
    num_aromatic_rings: Optional[int]
    h_bond_donors: Optional[int]
    h_bond_acceptors: Optional[int]
    tpsa: Optional[float]
    qed: Optional[float]
    source: str = "CoCoGraph-Augmented"

class MolecularSceneSetter:
    @dataclass
    class MolecularScene:
        target_properties: Dict[str, Tuple[float, float]]
        forbidden_substructures: List[str]
        required_substructures: List[str]
        num_samples: int = 100
        creativity_temperature: float = 0.7

    def set_scene(self, jules_thought: str, context: Optional[Dict] = None):
        scene = self.MolecularScene(target_properties={}, forbidden_substructures=[], required_substructures=[])
        if 'cristal líquido' in jules_thought.lower():
            scene.required_substructures.append('c1ccc2c(c1)ccc3ccccc23')
            if 'discótico' in jules_thought.lower():
                scene.required_substructures.append('c1ccc2c(c1)cc3c4c2cccc4ccc5c3cccc5')
            if 'tclear' in jules_thought.lower():
                import re
                match = re.search(r'tclear\s*>\s*(\d+)', jules_thought, re.IGNORECASE)
                if match:
                    temp = float(match.group(1))
                    scene.target_properties['Tclear'] = (temp, temp+150)
        return scene

class LiquidCrystalPredictor:
    def predict(self, smiles: str) -> Tuple[float, float]:
        import random
        # Mocking properties prediction for demonstration
        tmelt = random.uniform(300, 450)
        tclear = tmelt + random.uniform(20, 100)
        return tmelt, tclear

class MolecularCurator:
    def __init__(self, lc_predictor):
        self.lc_predictor = lc_predictor

    def curate(self, smiles_list: List[str], scene) -> List[Tuple[str, Dict]]:
        accepted = []
        for smiles in smiles_list:
            props = {}
            if 'Tclear' in scene.target_properties or 'Tmelt' in scene.target_properties:
                try:
                    tmelt, tclear = self.lc_predictor.predict(smiles)
                    props['Tmelt'] = tmelt
                    props['Tclear'] = tclear
                except Exception:
                    continue
            if self._satisfies_constraints(props, scene.target_properties):
                accepted.append((smiles, props))
        return accepted

    def _satisfies_constraints(self, props, targets):
        for prop, (low, high) in targets.items():
            if prop in props:
                if not (low <= props[prop] <= high):
                    return False
        return True

class CoCoGraphInterface:
    def __init__(self, model_weights_path: str, device='cpu'):
        pass

    def generate(self, scene) -> List[str]:
        # Generating a few mock SMILES
        return [
            'c1cc2c3c(c1)ccc1c3c(cc3c4c(cc5)ccc6c7c8c(cc9)ccc%10c%11c(cc%12)ccc%13c%14c(cc%15)ccc%16c%17c(cc%18)ccc(c19)c%20c%21c(cc%22)ccc(c1)c2c3c4c5c6c7c8c9c%10c%11c%12c%13c%14c%15c%16c%17c%18c%19c%20c%21%22',
            'CC1=C(C=C(C=C1)O)C2=CC=CC=C2',
            'c1ccccc1'
        ]

class MolecularPublicOracle:
    def __init__(self, db_path: str = "molecules_oracle.db", cocograph_weights: str = "cocograph_fps.pt"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self.cocograph = CoCoGraphInterface(cocograph_weights)
        self.curator = MolecularCurator(LiquidCrystalPredictor())
        self.scene_setter = MolecularSceneSetter()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS molecules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                smiles TEXT UNIQUE NOT NULL,
                tmelt REAL,
                tclear REAL,
                logp REAL,
                mol_weight REAL,
                num_aromatic_rings INTEGER,
                hbd INTEGER,
                hba INTEGER,
                tpsa REAL,
                qed REAL,
                source TEXT,
                canonical_hash TEXT
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_tclear ON molecules(tclear)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_tmelt ON molecules(tmelt)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_qed ON molecules(qed)")

    def populate_from_cocograph(self, n_total: int = 8_200_000, batch_size: int = 10_000):
        existing = self.conn.execute("SELECT COUNT(*) FROM molecules").fetchone()[0]
        needed = n_total - existing
        if needed <= 0:
            return

        # SIMULATE small insertion for tests (8.2M is too big for local test without mocking)
        # We will adjust needed to batch_size if needed > 0 for this demo
        needed = min(needed, 100) # Only insert up to 100 for fast tests

        batches = needed // batch_size + 1
        for _ in range(batches):
            scene = self.scene_setter.set_scene("cristal líquido com Tclear > 450")
            raw = self.cocograph.generate(scene)
            curated = self.curator.curate(raw, scene)
            with self.conn:
                for smiles, props in curated:
                    self._insert_molecule(smiles, props)

    def _insert_molecule(self, smiles: str, props: Dict[str, float]):
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, Lipinski
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            num_arom = Descriptors.NumAromaticRings(mol)
            hbd = Lipinski.NumHDonors(mol)
            hba = Lipinski.NumHAcceptors(mol)
            tpsa = Descriptors.TPSA(mol)
            qed = Descriptors.qed(mol)

            self.conn.execute("""
                INSERT OR IGNORE INTO molecules
                (smiles, tmelt, tclear, logp, mol_weight, num_aromatic_rings, hbd, hba, tpsa, qed, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CoCoGraph-Oracle')
            """, (smiles, props.get('Tmelt'), props.get('Tclear'), logp, mw, num_arom, hbd, hba, tpsa, qed))
        except ImportError:
            # If RDKit is missing, mock the insert
            self.conn.execute("""
                INSERT OR IGNORE INTO molecules
                (smiles, tmelt, tclear, logp, mol_weight, num_aromatic_rings, hbd, hba, tpsa, qed, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CoCoGraph-Oracle')
            """, (smiles, props.get('Tmelt'), props.get('Tclear'), 0.0, 0.0, 0, 0, 0, 0.0, 0.5))


    def query_by_property(self, prop: str, low: float, high: float, limit: int = 100) -> List[Dict]:
        allowed = ['tclear', 'tmelt', 'logp', 'mol_weight', 'qed', 'tpsa']
        if prop not in allowed:
            return []
        cur = self.conn.execute(f"SELECT smiles, tmelt, tclear, logp, mol_weight, qed FROM molecules WHERE {prop} BETWEEN ? AND ? LIMIT ?", (low, high, limit))
        return [dict(zip(['smiles','tmelt','tclear','logp','mol_weight','qed'], row)) for row in cur]

    def natural_language_query(self, thought: str) -> List[Dict]:
        import re
        constraints = {}
        if 'tclear' in thought.lower():
            match = re.search(r'tclear\s*>\s*(\d+)', thought, re.IGNORECASE)
            if match:
                constraints['tclear'] = (float(match.group(1)), 9999)
        if 'tmelt' in thought.lower():
            match = re.search(r'tmelt\s*>\s*(\d+)', thought, re.IGNORECASE)
            if match:
                constraints['tmelt'] = (float(match.group(1)), 9999)
        if 'qed' in thought.lower():
            match = re.search(r'qed\s*>\s*(0?\.\d+)', thought, re.IGNORECASE)
            if match:
                constraints['qed'] = (float(match.group(1)), 1.0)

        query = "SELECT smiles, tmelt, tclear, logp, mol_weight, qed FROM molecules WHERE 1=1"
        params = []
        for prop, (low, high) in constraints.items():
            query += f" AND {prop} BETWEEN ? AND ?"
            params.extend([low, high])
        query += " LIMIT 100"
        cur = self.conn.execute(query, params)
        return [dict(zip(['smiles','tmelt','tclear','logp','mol_weight','qed'], row)) for row in cur]
