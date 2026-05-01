import pytest
import numpy as np
from scripts.arkhe_sovereign_recursive_lattice_v159 import SovereignGlyphNode, RecursiveReactionDiffusionMesh

def test_sovereign_glyph_node_init():
    node = SovereignGlyphNode(0)
    assert node.id == 0
    assert node.agency_level == "sentience"
    assert len(node.state.shape) == 0  # It's a scalar complex number

def test_mesh_init():
    mesh = RecursiveReactionDiffusionMesh()
    assert len(mesh.nodes) == 22
    assert mesh.global_phase == 0.0
    assert not mesh.closed_loop

def test_recursive_step():
    mesh = RecursiveReactionDiffusionMesh()
    still_open = mesh.recursive_step()
    assert still_open is True or still_open is False
    assert mesh.global_phase > 0.0

def test_play_music_and_remember():
    mesh = RecursiveReactionDiffusionMesh()
    final_thought = mesh.play_music_and_remember(iterations=2)
    assert isinstance(final_thought, complex)
