"""Fusion360 V4 pre-check: never silently skip unsupported timeline entities."""

from __future__ import annotations

from typing import Any

ALLOWED_ENTITY_TYPES = frozenset({"Sketch", "ExtrudeFeature"})
UNSUPPORTED_ENTITY_TYPES = frozenset(
    {
        "RevolveFeature",
        "SweepFeature",
        "LoftFeature",
        "FilletFeature",
        "ChamferFeature",
        "ShellFeature",
        "MirrorFeature",
        "PatternFeature",
        "RectangularPatternFeature",
        "CircularPatternFeature",
        "HoleFeature",
        "ThreadFeature",
        "CombineFeature",
        "MoveFeature",
        "DraftFeature",
        "ScaleFeature",
    }
)
ALLOWED_EXTRUDE_OPS = frozenset(
    {"NewBodyFeatureOperation", "JoinFeatureOperation", "CutFeatureOperation"}
)


class Fusion360Unsupported(Exception):
    def __init__(self, reason: str, entity_type: str | None = None):
        self.reason = reason
        self.entity_type = entity_type
        super().__init__(reason)


def inspect_fusion360(data: dict) -> dict[str, Any]:
    entities = data.get("entities") or {}
    timeline = sorted(data.get("timeline") or [], key=lambda x: x.get("index", 0))
    types: list[str] = []
    extrude_ops: list[str] = []
    unsupported: list[str] = []
    n_extrude = 0
    n_intersect = 0
    for step in timeline:
        entity = entities.get(step.get("entity"))
        if entity is None:
            raise Fusion360Unsupported(f"missing_entity:{step.get('entity')}")
        et = str(entity.get("type") or "Unknown")
        types.append(et)
        if et in UNSUPPORTED_ENTITY_TYPES or (
            et not in ALLOWED_ENTITY_TYPES and et not in {"Sketch"}
        ):
            if et not in ALLOWED_ENTITY_TYPES:
                unsupported.append(et)
        if et == "ExtrudeFeature":
            n_extrude += 1
            op = entity.get("operation", "NewBodyFeatureOperation")
            extrude_ops.append(op)
            if op == "IntersectFeatureOperation":
                n_intersect += 1
                unsupported.append("IntersectFeatureOperation")
            elif op not in ALLOWED_EXTRUDE_OPS:
                unsupported.append(op)
    unique_unsup = sorted(set(unsupported))
    return {
        "n_timeline": len(timeline),
        "n_extrude": n_extrude,
        "n_intersect": n_intersect,
        "entity_types": sorted(set(types)),
        "extrude_ops": sorted(set(extrude_ops)),
        "unsupported": unique_unsup,
        "ok": n_extrude > 0 and not unique_unsup,
    }


def require_supported(data: dict) -> dict[str, Any]:
    info = inspect_fusion360(data)
    if info["unsupported"]:
        raise Fusion360Unsupported(
            "unsupported_operation:" + ",".join(info["unsupported"]),
            entity_type=info["unsupported"][0],
        )
    if info["n_extrude"] <= 0:
        raise Fusion360Unsupported("empty_extrude_sequence")
    return info
