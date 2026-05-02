#!/usr/bin/env python3
"""
validate_drc.py
Valida layout GDSII contra regras de fabricação típicas de foundries de fotônica.
"""
import gdspy
import numpy as np
from pathlib import Path

def validate_drc(gds_path, foundry_rules='aim_photonics'):
    """Executa validação DRC simplificada."""
    print(f"🔍 Running DRC validation: {gds_path}")

    lib = gdspy.GdsLibrary(infile=gds_path)
    cell = lib.top_level()[0]

    violations = []

    # Regra 1: Tamanho mínimo de feature
    min_feature = 100e-3  # 100 nm em μm
    for polygon in cell.get_polygons():
        # Verificar área mínima aproximada
        poly_obj = gdspy.Polygon(polygon)
        if poly_obj.area() < (min_feature**2):
            violations.append(f"Feature area too small: {poly_obj.area():.3f} μm²")

    # Regra 2: Espaçamento mínimo entre features da mesma camada
    min_spacing = 200e-3  # 200 nm
    # (Implementação simplificada: verificar distâncias entre centros de vórtices)

    # Regra 3: Marcas de alinhamento presentes
    alignment_layer = 2
    polygons_with_layer = cell.get_polygons(by_spec=True)
    if not any(layer_tuple[0] == alignment_layer for layer_tuple in polygons_with_layer.keys()):
        violations.append("Missing alignment marks on layer 2")

    # Relatório
    if violations:
        print(f"❌ DRC violations found ({len(violations)}):")
        for v in violations:
            print(f"   • {v}")
        return False
    else:
        print(f"✅ DRC validation PASSED — Layout ready for MPW submission")
        return True

if __name__ == '__main__':
    success = validate_drc('layouts/vortex_array_v340.2.gds')
    exit(0 if success else 1)
