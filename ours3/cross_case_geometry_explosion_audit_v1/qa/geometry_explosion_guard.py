"""Scale-relative geometry explosion guard.

Candidates with GEOMETRY_EXPLOSION_STATUS=REJECT are ineligible for TTS
and ineligible for best-available, even when OCC reports a valid BRep.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import yaml


def load_config(path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    text = yaml.dump(data)
    if "CASE_" in text:
        raise ValueError("geometry_explosion_guard.yaml must not contain case IDs")
    return data


def _arr(value) -> np.ndarray:
    return np.asarray(value, float).reshape(-1)


def expand_bbox(bbox_min, bbox_max, diag: float, margin_ratio: float) -> tuple[np.ndarray, np.ndarray]:
    lo = np.asarray(bbox_min, float)
    hi = np.asarray(bbox_max, float)
    pad = float(diag) * float(margin_ratio)
    return lo - pad, hi + pad


def _rate(flags) -> float:
    flags = np.asarray(flags, bool)
    if flags.size == 0:
        return 0.0
    return float(flags.mean())


def _outside(points, lo, hi) -> np.ndarray:
    pts = np.asarray(points, float).reshape(-1, 3)
    if pts.size == 0:
        return np.zeros(0, bool)
    return np.any((pts < lo) | (pts > hi), axis=1)


def bbox_metrics(cad_bbox: dict[str, Any], source: dict[str, Any]) -> dict[str, float]:
    src_diag = max(float(source["SOURCE_BBOX_DIAG"]), 1e-12)
    src_vol = max(float(source.get("SOURCE_BBOX_VOLUME") or 1e-12), 1e-12)
    cad_diag = float(cad_bbox.get("bbox_diag") or 0.0)
    cad_vol = float(cad_bbox.get("volume") or 0.0)
    return {
        "CAD_BBOX_DIAG": cad_diag,
        "CAD_BBOX_DIAG_RATIO": cad_diag / src_diag,
        "CAD_BBOX_VOLUME_RATIO": cad_vol / src_vol,
    }


def evaluate_edges(metrics: dict[str, Any], source_diag: float, cfg: dict[str, Any]) -> dict[str, Any]:
    src = max(float(source_diag), 1e-12)
    lengths = np.asarray(metrics.get("edge_lengths") or [metrics.get("max_edge_length") or 0.0], float)
    max_len = float(lengths.max()) if lengths.size else 0.0
    p95 = float(np.percentile(lengths, 95)) if lengths.size else 0.0
    long_ratio = float(cfg["edge"]["long_edge_ratio"])
    tiny_ratio = float(cfg["edge"]["tiny_edge_ratio"])
    return {
        "MAX_EDGE_LENGTH": max_len,
        "NORMALIZED_MAX_EDGE_LENGTH": max_len / src,
        "MAX_EDGE_LENGTH_RATIO": max_len / src,
        "P95_EDGE_LENGTH_RATIO": p95 / src,
        "LONG_EDGE_COUNT": int(np.sum(lengths > long_ratio * src)),
        "TINY_EDGE_COUNT": int(np.sum((lengths > 0) & (lengths < tiny_ratio * src))),
        "WIREFRAME_LONG_EDGE_COUNT": int(np.sum(lengths > long_ratio * src)),
    }


def evaluate_faces(metrics: dict[str, Any], source_diag: float, cfg: dict[str, Any]) -> dict[str, Any]:
    src = max(float(source_diag), 1e-12)
    diags = np.asarray(
        [row[2] for row in metrics.get("face_bboxes") or []] or [metrics.get("max_face_bbox_diag") or 0.0],
        float,
    )
    aspects = np.asarray(metrics.get("face_aspects") or [1.0], float)
    areas = np.asarray(metrics.get("face_areas") or [0.0], float)
    max_face = float(diags.max()) if diags.size else 0.0
    p95 = float(np.percentile(diags, 95)) if diags.size else 0.0
    extreme = float(cfg["face"]["extreme_aspect_ratio"])
    huge = float(cfg["face"]["huge_face_ratio"])
    degenerate = float(cfg["face"]["degenerate_area_ratio"]) * (src ** 2)
    extreme_count = int(np.sum(aspects >= extreme))
    n = max(int(aspects.size), 1)
    return {
        "MAX_FACE_BBOX_DIAG": max_face,
        "NORMALIZED_MAX_FACE_EXTENT": max_face / src,
        "MAX_FACE_EXTENT_RATIO": max_face / src,
        "P95_FACE_EXTENT_RATIO": p95 / src,
        "HUGE_FACE_COUNT": int(np.sum(diags > huge * src)),
        "EXTREME_ASPECT_RATIO_FACE_COUNT": extreme_count,
        "EXTREME_ASPECT_RATIO_FACE_RATE": extreme_count / n,
        "DEGENERATE_FACE_COUNT": int(np.sum(areas < degenerate)),
    }


def evaluate_control_net(metrics: dict[str, Any], source_diag: float, part_bbox: dict[str, Any] | None, cfg: dict[str, Any]) -> dict[str, Any]:
    src = max(float(source_diag), 1e-12)
    cp_bbox = metrics.get("control_point_bbox") or {}
    cp_diag = float(cp_bbox.get("bbox_diag") or 0.0)
    points = np.asarray(metrics.get("control_points") or [], float).reshape(-1, 3)
    part_lo = np.asarray((part_bbox or {}).get("bbox_min") or metrics.get("bbox_min") or [0, 0, 0], float)
    part_hi = np.asarray((part_bbox or {}).get("bbox_max") or metrics.get("bbox_max") or [0, 0, 0], float)
    outlier = 0.0
    if len(points):
        dx = np.maximum(part_lo - points, 0.0) + np.maximum(points - part_hi, 0.0)
        outlier = float(np.linalg.norm(dx, axis=1).max())
    return {
        "CONTROL_POINT_COUNT": int(metrics.get("control_point_count") or 0),
        "CONTROL_POINT_BBOX": cp_bbox,
        "CONTROL_POINT_BBOX_DIAG_RATIO": cp_diag / src,
        "CONTROL_POINT_BBOX_DIAG_RATIO_TO_PART": cp_diag / max(float((part_bbox or {}).get("bbox_diag") or src), 1e-12),
        "MAX_CONTROL_POINT_DISTANCE_TO_PART_BBOX": outlier,
        "CONTROL_NET_STEP_P95": float(metrics.get("control_net_step_p95") or 0.0),
        "CONTROL_NET_STEP_MAX": float(metrics.get("control_net_step_max") or 0.0),
        "CONTROL_NET_OUTLIER": bool(outlier > float(cfg["control_net"]["outlier_distance_ratio"]) * src),
    }


def evaluate_outside(metrics: dict[str, Any], source: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    lo, hi = expand_bbox(
        source["SOURCE_BBOX_MIN"],
        source["SOURCE_BBOX_MAX"],
        source["SOURCE_BBOX_DIAG"],
        cfg["source_bbox"]["expand_margin_ratio"],
    )
    verts = metrics.get("vertices") or []
    v_out = _outside(verts, lo, hi) if verts else np.zeros(0, bool)
    e_flags = []
    for elo, ehi, _length in metrics.get("edge_bboxes") or []:
        mid = (np.asarray(elo, float) + np.asarray(ehi, float)) * 0.5
        e_flags.append(bool(np.any((mid < lo) | (mid > hi))))
    f_flags = []
    for flo, fhi, *_rest in metrics.get("face_bboxes") or []:
        mid = (np.asarray(flo, float) + np.asarray(fhi, float)) * 0.5
        f_flags.append(bool(np.any((mid < lo) | (mid > hi))))
    return {
        "SOURCE_BBOX_EXPANDED": {"bbox_min": lo.tolist(), "bbox_max": hi.tolist()},
        "OUTSIDE_SOURCE_BBOX_VERTEX_RATE": _rate(v_out),
        "OUTSIDE_SOURCE_BBOX_EDGE_RATE": _rate(e_flags),
        "OUTSIDE_SOURCE_BBOX_FACE_RATE": _rate(f_flags),
    }


def infer_frame(declared: str | None, geometry_centroid, source_centroid, part_centroid) -> str:
    if declared:
        return str(declared)
    g = np.asarray(geometry_centroid or [0, 0, 0], float)
    s = np.asarray(source_centroid or [0, 0, 0], float)
    p = np.asarray(part_centroid or [0, 0, 0], float)
    if np.linalg.norm(g - p) < np.linalg.norm(g - s) * 0.5 + 1e-9:
        return "SOURCE_GLOBAL"
    if np.linalg.norm(g) < 1e-6 and np.linalg.norm(p) > 1e-3:
        return "PART_LOCAL"
    return "SOURCE_GLOBAL"


def evaluate_transform(pre_bbox: dict[str, Any] | None, post_bbox: dict[str, Any] | None, cfg: dict[str, Any]) -> dict[str, Any]:
    if not pre_bbox or not post_bbox:
        return {"TRANSFORM_SCALE_MISMATCH": False, "PLACED_TO_PREPLACEMENT_RATIO": 1.0}
    pre = max(float(pre_bbox.get("bbox_diag") or 0.0), 1e-12)
    post = float(post_bbox.get("bbox_diag") or 0.0)
    ratio = post / pre
    return {
        "TRANSFORM_SCALE_MISMATCH": bool(ratio > float(cfg["transform"]["scale_mismatch_reject_ratio"]) or ratio < 1.0 / float(cfg["transform"]["scale_mismatch_reject_ratio"])),
        "PLACED_TO_PREPLACEMENT_RATIO": float(ratio),
    }


def classify(metrics: dict[str, Any], cfg: dict[str, Any], part_diag: float | None = None) -> dict[str, Any]:
    reasons: list[str] = []
    warnings: list[str] = []

    def mark(cond_reject, cond_warn, code):
        if cond_reject:
            reasons.append(code)
        elif cond_warn:
            warnings.append(code)

    bbox_ratio = float(metrics.get("CAD_BBOX_DIAG_RATIO") or 0.0)
    mark(
        bbox_ratio >= cfg["bbox"]["reject_diag_ratio"],
        bbox_ratio >= cfg["bbox"]["warning_diag_ratio"],
        "BBOX_DIAG_RATIO_TOO_HIGH",
    )
    vol_ratio = float(metrics.get("CAD_BBOX_VOLUME_RATIO") or 0.0)
    mark(
        vol_ratio >= cfg["bbox"]["reject_volume_ratio"],
        vol_ratio >= cfg["bbox"]["warning_volume_ratio"],
        "BBOX_VOLUME_RATIO_TOO_HIGH",
    )
    edge_ratio = float(metrics.get("MAX_EDGE_LENGTH_RATIO") or 0.0)
    mark(
        edge_ratio >= cfg["edge"]["reject_max_ratio"] or int(metrics.get("LONG_EDGE_COUNT") or 0) >= 3 and edge_ratio >= cfg["edge"]["long_edge_ratio"],
        edge_ratio >= cfg["edge"]["warning_max_ratio"],
        "LONG_EDGE",
    )
    face_ratio = float(metrics.get("MAX_FACE_EXTENT_RATIO") or 0.0)
    mark(
        face_ratio >= cfg["face"]["reject_max_extent_ratio"],
        face_ratio >= cfg["face"]["warning_max_extent_ratio"] or int(metrics.get("HUGE_FACE_COUNT") or 0) >= 2,
        "HUGE_FACE",
    )
    aspect_rate = float(metrics.get("EXTREME_ASPECT_RATIO_FACE_RATE") or 0.0)
    # High aspect faces are common on valid skins/wings. Reject only when
    # they co-occur with a true scale explosion.
    scale_exploded = bbox_ratio >= cfg["bbox"]["reject_diag_ratio"] or float(metrics.get("OUTSIDE_SOURCE_BBOX_FACE_RATE") or 0.0) >= cfg["outside"]["reject_face_rate"]
    mark(
        aspect_rate >= cfg["face"]["reject_extreme_aspect_rate"] and scale_exploded and int(metrics.get("EXTREME_ASPECT_RATIO_FACE_COUNT") or 0) >= 2,
        aspect_rate >= cfg["face"]["warning_extreme_aspect_rate"],
        "EXTREME_ASPECT_RATIO",
    )
    mark(
        float(metrics.get("OUTSIDE_SOURCE_BBOX_FACE_RATE") or 0.0) >= cfg["outside"]["reject_face_rate"]
        or float(metrics.get("OUTSIDE_SOURCE_BBOX_VERTEX_RATE") or 0.0) >= cfg["outside"]["reject_vertex_rate"],
        float(metrics.get("OUTSIDE_SOURCE_BBOX_FACE_RATE") or 0.0) >= cfg["outside"]["warning_face_rate"],
        "OUTSIDE_SOURCE_BBOX",
    )
    cp_ratio = float(metrics.get("CONTROL_POINT_BBOX_DIAG_RATIO") or 0.0)
    mark(
        bool(metrics.get("CONTROL_NET_OUTLIER")) or cp_ratio >= cfg["control_net"]["reject_diag_ratio"],
        cp_ratio >= cfg["control_net"]["warning_diag_ratio"],
        "CONTROL_NET_OUT_OF_RANGE",
    )
    if metrics.get("TRANSFORM_SCALE_MISMATCH"):
        reasons.append("TRANSFORM_SCALE_MISMATCH")
    if part_diag:
        cad_to_part = float(metrics.get("CAD_BBOX_DIAG") or 0.0) / max(float(part_diag), 1e-12)
        metrics["CAD_TO_PART_DIAG_RATIO"] = cad_to_part
        mark(
            cad_to_part >= cfg["part_relative"]["reject_cad_to_part_diag_ratio"],
            cad_to_part >= cfg["part_relative"]["warning_cad_to_part_diag_ratio"],
            "PART_RELATIVE_BBOX_EXPLOSION",
        )
    if metrics.get("SURFACE_DOMAIN_EXPLOSION"):
        reasons.append("LOFT_DOMAIN_ERROR")
    if metrics.get("LOFT_PREFLIGHT_PASS") is False:
        reasons.append("LOFT_PREFLIGHT_FAILED")
    if int(metrics.get("pcurve_domain_error_count") or 0) > 0:
        reasons.append("PCURVE_DOMAIN_ERROR")

    unique_reasons = list(dict.fromkeys(reasons))
    unique_warnings = [w for w in dict.fromkeys(warnings) if w not in unique_reasons]
    if unique_reasons:
        status = "REJECT"
    elif unique_warnings:
        status = "WARNING"
    else:
        status = "PASS"
    exploded = status == "REJECT"
    return {
        "GEOMETRY_EXPLOSION_STATUS": status,
        "GEOMETRY_EXPLOSION_REASONS": unique_reasons,
        "GEOMETRY_EXPLOSION_WARNINGS": unique_warnings,
        "ELIGIBLE_FOR_TTS": not exploded,
        "ELIGIBLE_FOR_BEST_AVAILABLE": not exploded,
        **metrics,
    }


def evaluate_candidate(
    occ_metrics: dict[str, Any],
    source: dict[str, Any],
    cfg: dict[str, Any],
    part_bbox: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {}
    payload.update(bbox_metrics(occ_metrics, source))
    payload.update(evaluate_edges(occ_metrics, source["SOURCE_BBOX_DIAG"], cfg))
    payload.update(evaluate_faces(occ_metrics, source["SOURCE_BBOX_DIAG"], cfg))
    payload.update(evaluate_control_net(occ_metrics, source["SOURCE_BBOX_DIAG"], part_bbox, cfg))
    payload.update(evaluate_outside(occ_metrics, source, cfg))
    payload["pcurve_domain_error_count"] = int(occ_metrics.get("pcurve_domain_error_count") or 0)
    payload["bbox_min"] = occ_metrics.get("bbox_min")
    payload["bbox_max"] = occ_metrics.get("bbox_max")
    payload["centroid"] = occ_metrics.get("centroid")
    payload["entity_count"] = occ_metrics.get("entity_count")
    payload["edge_count"] = occ_metrics.get("edge_count")
    payload["face_count"] = occ_metrics.get("face_count")
    if extra:
        payload.update(extra)
    part_diag = float((part_bbox or {}).get("bbox_diag") or 0.0) or None
    return classify(payload, cfg, part_diag=part_diag)
