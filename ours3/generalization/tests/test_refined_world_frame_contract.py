from __future__ import annotations

import numpy as np

from generalization.frame_contract import (
    apply_transform,
    axis_angle_error,
    compose,
    inverse_error,
)


def rigid_translation(x, y, z):
    matrix = np.eye(4)
    matrix[:3, 3] = [x, y, z]
    return matrix


def rigid_z_rotation(angle):
    matrix = np.eye(4)
    c, s = np.cos(angle), np.sin(angle)
    matrix[:3, :3] = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    return matrix


def test_identity_transform_roundtrip():
    points = np.array([[0.0, 1.0, 2.0], [2.0, 0.0, -1.0]])
    identity = np.eye(4)
    assert np.allclose(apply_transform(apply_transform(points, identity), identity), points)


def test_translation_roundtrip():
    points = np.array([[0.0, 1.0, 2.0], [2.0, 0.0, -1.0]])
    transform = rigid_translation(3.0, -2.0, 5.0)
    restored = apply_transform(apply_transform(points, transform), np.linalg.inv(transform))
    assert np.max(np.abs(restored - points)) < 1e-12


def test_rotation_roundtrip():
    points = np.array([[0.0, 1.0, 2.0], [2.0, 0.0, -1.0]])
    transform = rigid_z_rotation(0.73)
    restored = apply_transform(apply_transform(points, transform), np.linalg.inv(transform))
    assert np.max(np.abs(restored - points)) < 1e-12
    assert axis_angle_error(transform, transform) < 1e-12


def test_nested_frame_roundtrip():
    coarse_to_world = compose(rigid_z_rotation(0.4), rigid_translation(3, -2, 5))
    refined_to_coarse = compose(rigid_z_rotation(-0.2), rigid_translation(1, 4, 0))
    refined_to_world = coarse_to_world @ refined_to_coarse
    points = np.array([[0.2, 0.3, 0.4], [2.0, -1.0, 0.5]])
    world = apply_transform(points, refined_to_world)
    restored = apply_transform(world, np.linalg.inv(refined_to_world))
    assert np.max(np.abs(restored - points)) < 1e-12


def test_inverse_pair_and_wrong_inverse_detection():
    transform = compose(rigid_z_rotation(0.6), rigid_translation(1, 2, 3))
    assert inverse_error(transform, np.linalg.inv(transform)) < 1e-12
    assert inverse_error(transform, transform) > 1e-3
