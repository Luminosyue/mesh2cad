from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SemanticRoleAdapter:
    ontology: dict[str, dict[str, Any]]

    def adapt(self, raw_name: str | None, description: str | None, geometry: dict[str, Any]) -> dict[str, Any]:
        text = " ".join(value for value in (raw_name, description) if value).strip().lower()
        best = None
        best_score = 0.0
        for role, spec in self.ontology.items():
            score = max((1.0 for token in spec.get("keywords", []) if token.lower() in text), default=0.0)
            if score and score > best_score:
                best = role
                best_score = score
        if best is None:
            role = "UNKNOWN"
            family = "UNKNOWN"
            confidence = 0.0
        else:
            role = best
            family = str(self.ontology[best].get("role_family", "UNKNOWN"))
            confidence = min(1.0, 0.45 + 0.1 * best_score + 0.2 * float(geometry.get("semantic_support", 0.0)))
        conflict = bool(role != "UNKNOWN" and geometry.get("geometry_class") == "UNKNOWN")
        return {
            "semantic_role": role,
            "role_family": family,
            "semantic_confidence": confidence,
            "semantic_geometry_conflict": conflict,
            "raw_name": raw_name,
            "raw_description": description,
        }

