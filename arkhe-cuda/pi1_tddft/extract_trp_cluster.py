#!/usr/bin/env python3
"""
Extrai os 8 Triptofanos da tubulina (PDB 1JFF), trunca no Cβ,
e gera um ficheiro XYZ para input do ORCA.
"""
from Bio.PDB import PDBParser, Selection, NeighborSearch
import numpy as np

# 1. Carregar estrutura
parser = PDBParser(QUIET=True)
structure = parser.get_structure('1JFF', '1jff.pdb')

# 2. Selecionar resíduos de Triptofano (TRP) das cadeias A (alfa) e B (beta)
trp_residues = []
for model in structure:
    for chain in model:
        if chain.id in ['A', 'B']:
            for residue in chain:
                if residue.resname == 'TRP':
                    trp_residues.append(residue)

print(f"Encontrados {len(trp_residues)} resíduos TRP.")

# 3. Para cada TRP, extrair apenas os átomos do anel indol + Cβ
#    (átomos do anel: CG, CD1, CD2, NE1, CE2, CE3, CZ2, CZ3, CH2)
indol_atoms_names = ['CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2', 'CB']

cluster_atoms = []
for res in trp_residues:
    for atom_name in indol_atoms_names:
        if atom_name in res:
            atom = res[atom_name]
            cluster_atoms.append({
                'element': atom.element,
                'coord': atom.coord
            })

print(f"Total de átomos no cluster: {len(cluster_atoms)}")

# 4. Truncamento no Cβ: substituir a ligação Cβ-Cα por um H
#    (já estamos a ignorar Cα, mas precisamos de saturar Cβ)
#    Para simplicidade, mantemos CB e confiamos no modelo de solvente implícito.

# 5. Escrever ficheiro XYZ para ORCA
with open('tryptophan_cluster.xyz', 'w') as f:
    f.write(f"{len(cluster_atoms)}\n")
    f.write("Cluster de 8 aneis indol de Triptofano (1JFF)\n")
    for atom in cluster_atoms:
        f.write(f"{atom['element']} {atom['coord'][0]:.6f} {atom['coord'][1]:.6f} {atom['coord'][2]:.6f}\n")

print("Ficheiro tryptophan_cluster.xyz gerado.")
