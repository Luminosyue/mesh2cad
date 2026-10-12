from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import trimesh


@dataclass
class PropellerPatternEvidence:
    rotation_axis: np.ndarray
    hub_region: dict[str, Any]
    hub_component_evidence: bool
    blade_correspondence_evidence: bool
    blade_count: int
    blade_angular_positions_deg: list[float]
    blade_roots: list[list[float]]
    blade_tips: list[list[float]]
    blade_length: float | None
    blade_width_profile: list[float]
    blade_taper: float | None
    blade_sweep: float | None
    blade_twist_evidence: float | None
    evidence_sufficient: bool
    insufficiency_reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "rotation_axis": self.rotation_axis.tolist(),
            "hub_region": self.hub_region,
            "hub_component_evidence": self.hub_component_evidence,
            "blade_correspondence_evidence": self.blade_correspondence_evidence,
            "blade_count": self.blade_count,
            "blade_angular_positions_deg": self.blade_angular_positions_deg,
            "blade_roots": self.blade_roots,
            "blade_tips": self.blade_tips,
            "blade_length": self.blade_length,
            "blade_width_profile": self.blade_width_profile,
            "blade_taper": self.blade_taper,
            "blade_sweep": self.blade_sweep,
            "blade_twist_evidence": self.blade_twist_evidence,
            "evidence_sufficient": self.evidence_sufficient,
            "insufficiency_reason": self.insufficiency_reason,
        }


class PropellerPatternAnalyzer:
    """Deterministic geometry-only evidence extractor.

    It never invents blades or placements. It only reports whether the source
    mesh contains enough connected-component and rotational evidence to justify
    a generic patterned-freeform reconstruction.
    """

    def analyze(self, mesh: trimesh.Trimesh) -> PropellerPatternEvidence:
        components = sorted(mesh.split(only_watertight=False), key=lambda item: -item.area)
        vertices = np.asarray(mesh.vertices, dtype=float)
        covariance = np.cov(vertices - vertices.mean(axis=0), rowvar=False)
        values, vectors = np.linalg.eigh(covariance)
        rotation_axis = vectors[:, int(np.argmin(values))]
        rotation_axis /= max(float(np.linalg.norm(rotation_axis)), 1e-12)

        centers = [np.asarray(part.centroid, dtype=float) for part in components]
        origin = np.mean(centers, axis=0) if centers else mesh.centroid
        radial = []
        for center in centers:
            offset = center - origin
            offset = offset - np.dot(offset, rotation_axis) * rotation_axis
            if np.linalg.norm(offset) > 1e-9:
                radial.append(offset / np.linalg.norm(offset))
        basis = radial[0] if radial else np.array([1.0, 0.0, 0.0])
        second = np.cross(rotation_axis, basis)
        angles = []
        for vector in radial:
            angles.append(float(np.degrees(np.arctan2(np.dot(vector, second), np.dot(vector, basis))) % 360.0))

        roots = []
        tips = []
        lengths = []
        widths = []
        for part in components:
            part_vertices = np.asarray(part.vertices, dtype=float)
            projection = part_vertices @ basis
            root = part_vertices[int(np.argmin(projection))]
            tip = part_vertices[int(np.argmax(projection))]
            roots.append(root.tolist())
            tips.append(tip.tolist())
            lengths.append(float(np.linalg.norm(tip - root)))
            widths.append(float(np.max(part.extents)))

        blade_count = len(components)
        angular_span = 0.0
        if len(angles) > 1:
            ordered = sorted(angles)
            gaps = np.diff(ordered + [ordered[0] + 360.0])
            angular_span = float(np.std(gaps))
        blade_correspondence_evidence = bool(
            blade_count >= 2
            and len(angles) == blade_count
            and angular_span < 25.0
            and all(length > 1e-4 for length in lengths)
        )
        # A generic rotational builder must be grounded by a separately
        # observed hub region. Two disconnected blade-like components alone
        # are not enough to infer the hub boundary or a safe local attachment.
        hub_component_evidence = bool(len(components) >= 3)
        evidence_sufficient = bool(
            hub_component_evidence and blade_correspondence_evidence
        )
        if evidence_sufficient:
            reason = ""
        elif not hub_component_evidence:
            reason = (
                "HUB_COMPONENT_NOT_OBSERVED: source Part Mesh exposes "
                f"{len(components)} disconnected component(s); a generic "
                "pattern builder requires an independently observed hub region"
            )
        else:
            reason = (
                "BLADE_CORRESPONDENCE_INSUFFICIENT: rotational repetition, "
                "blade roots/tips, or blade lengths are not sufficiently "
                "constrained for a generic pattern builder"
            )
        return PropellerPatternEvidence(
            rotation_axis=rotation_axis,
            hub_region={
                "component_count": len(components),
                "centroid": origin.tolist(),
                "hub_component_evidence": hub_component_evidence,
            },
            hub_component_evidence=hub_component_evidence,
            blade_correspondence_evidence=blade_correspondence_evidence,
            blade_count=blade_count,
            blade_angular_positions_deg=angles,
            blade_roots=roots,
            blade_tips=tips,
            blade_length=float(np.mean(lengths)) if lengths else None,
            blade_width_profile=widths,
            blade_taper=None,
            blade_sweep=None,
            blade_twist_evidence=None,
            evidence_sufficient=evidence_sufficient,
            insufficiency_reason=reason,
        )
