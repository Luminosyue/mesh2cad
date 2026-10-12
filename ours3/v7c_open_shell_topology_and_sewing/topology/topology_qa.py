"""Topology identity, incidence and duplicate-coincident-edge QA."""

from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS


def face_edges(face):
    edges, explorer = [], TopExp_Explorer(face, TopAbs_EDGE)
    while explorer.More():
        edges.append(TopoDS.Edge_s(explorer.Current()))
        explorer.Next()
    return edges


def incidence(shape):
    unique, counts = [], []
    faces, explorer = [], TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        faces.append(TopoDS.Face_s(explorer.Current()))
        explorer.Next()
    for face in faces:
        for edge in face_edges(face):
            match = next((index for index, old in enumerate(unique) if edge.IsSame(old)), None)
            if match is None:
                unique.append(edge); counts.append(1)
            else:
                counts[match] += 1
    return unique, counts


def identity_shared(edge, face_a, face_b):
    return any(edge.IsSame(item) for item in face_edges(face_a)) and any(edge.IsSame(item) for item in face_edges(face_b))


def duplicate_coincident_count(shape, threshold):
    edges, counts = incidence(shape)
    samples = []
    for edge in edges:
        curve = BRepAdaptor_Curve(edge)
        params = np.linspace(curve.FirstParameter(), curve.LastParameter(), 65)
        samples.append(np.asarray([[curve.Value(float(t)).X(), curve.Value(float(t)).Y(), curve.Value(float(t)).Z()] for t in params]))
    duplicates = 0
    for i in range(len(samples)):
        for j in range(i + 1, len(samples)):
            if edges[i].IsSame(edges[j]):
                continue
            distances = np.r_[cKDTree(samples[j]).query(samples[i])[0], cKDTree(samples[i]).query(samples[j])[0]]
            if distances.max() <= threshold:
                duplicates += 1
    return duplicates
