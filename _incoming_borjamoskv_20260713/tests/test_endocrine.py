# [C5-REAL] Exergy-Maximized
"""
Unit tests for the Volumetric Endocrinology system in Teorema-Robinson-Moskv.
Mathematically verifies linear decay of waves, R-limit boundary cutoff, and node management.
"""

import math
from cortex.engine.endocrine import VolumetricEndocrinology


def test_volumetric_math_decay():
    # Instantiate with radius limit R = 20.0
    R = 20.0
    engine = VolumetricEndocrinology(radius_limit=R)

    # Emitter position
    engine.register_agent("node_emitter", 0.0, 0.0, 0.0)

    # Node exactly 12.0 units away
    # pos = (0, 12, 0) -> distance = 12.0
    engine.register_agent("node_close", 0.0, 12.0, 0.0)

    # Node exactly 20.0 units away (on the boundary)
    # pos = (12, 16, 0) -> distance = math.sqrt(12^2 + 16^2) = math.sqrt(144 + 256) = 20.0
    engine.register_agent("node_boundary", 12.0, 16.0, 0.0)

    # Node 25.0 units away (outside boundary)
    engine.register_agent("node_far", 15.0, 20.0, 0.0)

    # Initial states should be 0.1
    assert engine.get_node_state("node_close")["dopamine"] == 0.1
    assert engine.get_node_state("node_boundary")["dopamine"] == 0.1
    assert engine.get_node_state("node_far")["dopamine"] == 0.1

    # Emit dopamine wave from emitter with intensity 0.8
    intensity = 0.8
    engine.emit_hormone_wave("node_emitter", "dopamine", intensity)

    # close node: dist = 12.0. Decay = 1.0 - (12.0 / 20.0) = 0.4
    # Applied signal = 0.8 * 0.4 = 0.32. New dopamine = 0.1 (base) + 0.32 = 0.42
    close_state = engine.get_node_state("node_close")
    assert math.isclose(close_state["dopamine"], 0.42, abs_tol=1e-4)

    # boundary node: dist = 20.0. Decay = 1.0 - (20.0 / 20.0) = 0.0
    # Applied signal = 0.0. New dopamine should remain 0.1
    boundary_state = engine.get_node_state("node_boundary")
    assert math.isclose(boundary_state["dopamine"], 0.1, abs_tol=1e-4)

    # far node: dist = 25.0 (> R). Dopamine should remain 0.1
    far_state = engine.get_node_state("node_far")
    assert far_state["dopamine"] == 0.1


def test_cortisol_wave_emission():
    # Instantiate with radius limit R = 10.0
    engine = VolumetricEndocrinology(radius_limit=10.0)

    # Register emitter and receiver
    engine.register_agent("sender", 0.0, 0.0, 0.0)
    engine.register_agent("receiver", 6.0, 0.0, 8.0)  # dist = 10.0

    # Emit cortisol wave
    engine.emit_hormone_wave("sender", "cortisol", 0.5)

    # Receiver is on the boundary (dist = 10.0), so applied cortisol should be 0
    receiver_state = engine.get_node_state("receiver")
    assert receiver_state["cortisol"] == 0.1


def test_fail_silent_missing_emitter():
    engine = VolumetricEndocrinology(radius_limit=10.0)
    # Should not raise exception
    engine.emit_hormone_wave("nonexistent_emitter", "dopamine", 1.0)
