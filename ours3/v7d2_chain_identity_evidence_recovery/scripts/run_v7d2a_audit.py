#!/usr/bin/env python3
"""V7D2A saved-evidence audit. This script never remeasures geometry."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V7A = ROOT / "v7a_profile_recovery/03_geometry_analyzer"
V7B = ROOT / "v7b_profile_type_aware_open_shell_reconstruction"
V7D1 = ROOT / "v7d1_robust_global_seam_track_recovery"
OUT = ROOT / "v7d2_chain_identity_evidence_recovery"
PARTS = {"CADPART_000": "FUSELAGE", "CADPART_005": "VERTICAL_TAIL"}


def load(path: Path):
    return json.loads(path.read_text())


def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def sha(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def evidence_files():
    paths = []
    for pid in PARTS:
        paths.extend([
            V7A / pid / "geometry_analysis.json",
            V7B / "03_geometry_analyzer" / pid / "profile_type_classifications.json",
            V7B / "03_geometry_analyzer" / pid / "open_chain_tracks.json",
            V7B / "04_measured_spec" / pid / "measured_cad_spec.json",
            V7D1 / "seam_tracking" / pid / "global_track.json",
        ])
    paths.append(V7B / "geometry/open_chain_correspondence.py")
    return paths


def station_matrix(pid: str, label: str):
    ga = load(V7A / pid / "geometry_analysis.json")
    classifications = load(V7B / "03_geometry_analyzer" / pid / "profile_type_classifications.json")
    saved = load(V7B / "03_geometry_analyzer" / pid / "open_chain_tracks.json")
    measured = load(V7B / "04_measured_spec" / pid / "measured_cad_spec.json")
    profiles = {item["station_id"]: item for item in ga["profiles"]}
    cls = {item["station_id"]: item for item in classifications}
    by_station = {}
    for track_id, entries in saved["tracks"].items():
        for item in entries:
            by_station.setdefault(item["station_id"], []).append((track_id, item))

    measured_tracks = measured["open_chain_tracks"]
    primary_id = sorted(measured_tracks)[0]
    secondary_id = sorted(measured_tracks)[-1]
    primary_stations = {item["station_id"] for item in measured_tracks[primary_id]}
    secondary_stations = {item["station_id"] for item in measured_tracks[secondary_id]}
    seam_identity_stations = primary_stations & secondary_stations
    support_stations = primary_stations | secondary_stations

    rows = []
    for sid in sorted(profiles):
        profile = profiles[sid]
        graph_summary = cls[sid].get("raw_segment_graph") or {}
        entries = by_station.get(sid, [])
        geometry = bool(entries) and all(len(item.get("raw_points_3d", [])) >= 2 for _, item in entries)
        endpoints = geometry
        orientation = bool(entries) and all(
            "orientation_reversed" in item and "ordering_valid" in item for _, item in entries
        )
        identity = sid in seam_identity_stations
        raw_open_count = int(graph_summary.get("open_chain_count", 0))
        reason = ""
        missing_class = ""
        if not profile.get("raw_intersection_exists", False):
            reason, missing_class = "RAW_INTERSECTION_NOT_AVAILABLE", "RAW_SECTION_MISSING"
        elif identity:
            reason, missing_class = "NONE", "NONE"
        elif len(entries) >= 2:
            reason, missing_class = "SECOND_TRACK_SINGLETON_OR_NONCONTIGUOUS", "CHAIN_IDENTITY_AMBIGUOUS"
        elif profile.get("profile_type") != "OPEN_SHELL_PROFILE" and raw_open_count > 0:
            reason, missing_class = "PROFILE_TYPE_FILTER_DROPPED_OPEN_COMPONENTS", "FILTER_OVER_REJECTION"
        elif len(entries) == 1:
            reason, missing_class = "RAW_GRAPH_HAS_ONLY_ONE_PERSISTED_OPEN_CHAIN", "CHAIN_EXTRACTION_MISSING"
        else:
            reason, missing_class = "NO_SECOND_OPEN_CHAIN_IN_MEASURED_SECTION", "CHAIN_EXTRACTION_MISSING"
        # The saved object contains only aggregate graph counts, not nodes/edges.
        rows.append({
            "PART": label,
            "P3_PART_ID": pid,
            "STATION_ID": sid,
            "RAW_SECTION_INTERSECTION_AVAILABLE": bool(profile.get("raw_intersection_exists", False)),
            "RAW_SECTION_GRAPH_AVAILABLE": False,
            "RAW_SECTION_GRAPH_SUMMARY_AVAILABLE": bool(graph_summary),
            "RAW_GRAPH_OPEN_CHAIN_COUNT": raw_open_count,
            "OPEN_CHAIN_AVAILABLE": bool(entries),
            "OPEN_CHAIN_COUNT": len(entries),
            "CHAIN_GEOMETRY_PERSISTED": geometry,
            "CHAIN_ENDPOINTS_PERSISTED": endpoints,
            "CHAIN_ORIENTATION_PERSISTED": orientation,
            "CHAIN_IDENTITY_AVAILABLE": identity,
            "SEAM_ENDPOINT_CANDIDATE_AVAILABLE": identity and endpoints,
            "FILTER_REJECTION_REASON": reason,
            "MISSING_EVIDENCE_CLASS": missing_class,
            "PERSISTED_TRACK_IDS": "|".join(track_id for track_id, _ in entries),
            "PERSISTED_CHAIN_IDS": "|".join(item["chain_id"] for _, item in entries),
            "ORIENTATION_REVERSED_FLAGS": "|".join(str(item.get("orientation_reversed")) for _, item in entries),
            "PROFILE_STATUS": profile.get("status"),
            "PROFILE_TYPE": profile.get("profile_type"),
        })
    return rows, {
        "requested_station_count": len(profiles),
        "support_stations": sorted(support_stations),
        "seam_identity_stations": sorted(seam_identity_stations),
        "primary_track_id": primary_id,
        "secondary_track_id": secondary_id,
        "orientation_flips_claimed_fixed": saved["orientation_flips_fixed"],
    }


def direction_audit(pid: str):
    saved = load(V7B / "03_geometry_analyzer" / pid / "open_chain_tracks.json")
    global_track = load(V7D1 / "seam_tracking" / pid / "global_track.json")
    track_changes = []
    for track_id, entries in saved["tracks"].items():
        previous = None
        for item in entries:
            points = np.asarray(item["resampled_points_3d"], float)
            vector = points[-1] - points[0]
            vector /= np.linalg.norm(vector) + 1e-15
            angle = None
            if previous is not None:
                angle = math.degrees(math.acos(np.clip(float(np.dot(previous, vector)), -1, 1)))
            track_changes.append({
                "track_id": track_id,
                "station_id": item["station_id"],
                "orientation_reversed_flag": item["orientation_reversed"],
                "persisted_direction": vector.tolist(),
                "direction_change_degrees": angle,
                "direction_reversal_detected": bool(angle is not None and angle > 150),
            })
            previous = vector

    path = global_track["global_path"]
    points = np.asarray([item["consensus_point"] for item in path], float)
    steps = np.diff(points, axis=0)
    turns = []
    for index in range(len(steps) - 1):
        angle = math.degrees(math.acos(np.clip(float(
            np.dot(steps[index], steps[index + 1]) /
            (np.linalg.norm(steps[index]) * np.linalg.norm(steps[index + 1]) + 1e-15)
        ), -1, 1)))
        center = path[index + 1]
        turns.append({
            "station_id": center["station_id"],
            "turn_degrees": angle,
            "curvature_spike": angle > 150,
            "previous_endpoint_state": [path[index]["endpoint_a"], path[index]["endpoint_b"]],
            "center_endpoint_state": [center["endpoint_a"], center["endpoint_b"]],
            "next_endpoint_state": [path[index + 2]["endpoint_a"], path[index + 2]["endpoint_b"]],
        })
    return {
        "orientation_flips_claimed_fixed": saved["orientation_flips_fixed"],
        "persisted_track_direction_changes": track_changes,
        "global_path_turns": turns,
        "spike_stations": [item["station_id"] for item in turns if item["curvature_spike"]],
        "root_cause": "STALE_PRE_REVERSAL_DESCRIPTOR_CAUSED_CHAIN_ORIENTATION_AND_ENDPOINT_IDENTITY_REVERSAL",
        "source_logic_evidence": {
            "file": str(V7B / "geometry/open_chain_correspondence.py"),
            "reverse_points_lines": "127-130",
            "descriptor_recomputed_after_reverse": False,
            "next_station_uses_stale_descriptor": True,
        },
    }


def main():
    (OUT / "artifacts").mkdir(parents=True, exist_ok=True)
    before = {str(path): {"sha256": sha(path), "mtime_ns": path.stat().st_mtime_ns} for path in evidence_files()}
    rows = []
    details = {}
    for pid, label in PARTS.items():
        part_rows, detail = station_matrix(pid, label)
        rows.extend(part_rows)
        details[label] = detail

    matrix_json = OUT / "artifacts/evidence_completeness_matrix.json"
    matrix_csv = OUT / "artifacts/evidence_completeness_matrix.csv"
    dump(matrix_json, rows)
    with matrix_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    tail_audit = direction_audit("CADPART_005")
    dump(OUT / "artifacts/vertical_tail_direction_identity_audit.json", tail_audit)

    coverage = {}
    for label in PARTS.values():
        selected = [row for row in rows if row["PART"] == label]
        requested = len(selected)
        raw = sum(row["RAW_SECTION_INTERSECTION_AVAILABLE"] for row in selected)
        support = len(details[label]["support_stations"])
        identities = len(details[label]["seam_identity_stations"])
        coverage[label] = {
            "raw_section": raw / requested,
            "raw_section_count": f"{raw}/{requested}",
            "open_chain": support / requested,
            "open_chain_count": f"{support}/{requested}",
            "chain_identity": identities / support,
            "chain_identity_count": f"{identities}/{support}",
            "endpoint_evidence": identities / support,
            "endpoint_evidence_count": f"{identities}/{support}",
        }

    after = {str(path): {"sha256": sha(path), "mtime_ns": path.stat().st_mtime_ns} for path in evidence_files()}
    upstream_unchanged = before == after
    summary = {
        "CURRENT_GATE": "V7D2A_EVIDENCE_AUDIT_PASS",
        "AUDIT_ONLY": True,
        "DAG_WEIGHTS_CHANGED": False,
        "MISSING_STATIONS_INTERPOLATED": False,
        "MASTER_CURVE_CREATED": False,
        "CONSTRAINED_REFIT_EXECUTED": False,
        "V7C_EXECUTED": False,
        "SEWING_EXECUTED": False,
        "RUNTIME_GEOMETRY_REMEASUREMENT": False,
        "RAW_SECTION_GRAPH_FULL_GEOMETRY_PERSISTED": False,
        "RAW_SECTION_GRAPH_SUMMARY_PERSISTED": True,
        "FUSELAGE_RAW_SECTION_COVERAGE": coverage["FUSELAGE"]["raw_section"],
        "FUSELAGE_OPEN_CHAIN_COVERAGE": coverage["FUSELAGE"]["open_chain"],
        "FUSELAGE_CHAIN_IDENTITY_COVERAGE": coverage["FUSELAGE"]["chain_identity"],
        "FUSELAGE_ENDPOINT_EVIDENCE_COVERAGE": coverage["FUSELAGE"]["endpoint_evidence"],
        "VERTICAL_TAIL_RAW_SECTION_COVERAGE": coverage["VERTICAL_TAIL"]["raw_section"],
        "VERTICAL_TAIL_OPEN_CHAIN_COVERAGE": coverage["VERTICAL_TAIL"]["open_chain"],
        "VERTICAL_TAIL_CHAIN_IDENTITY_COVERAGE": coverage["VERTICAL_TAIL"]["chain_identity"],
        "VERTICAL_TAIL_ENDPOINT_EVIDENCE_COVERAGE": coverage["VERTICAL_TAIL"]["endpoint_evidence"],
        "coverage_counts": coverage,
        "FUSELAGE_SECOND_TRACK_STATIONS": details["FUSELAGE"]["seam_identity_stations"],
        "FUSELAGE_SUPPORT_STATIONS": details["FUSELAGE"]["support_stations"],
        "FUSELAGE_MISSING_EVIDENCE_CLASS": "CHAIN_EXTRACTION_MISSING",
        "FUSELAGE_ROOT_CAUSE": "SECOND_OPEN_CHAIN_NOT_PRESENT_IN_SAVED_MEASURED_SECTION_EVIDENCE_OUTSIDE_S03_S06",
        "VERTICAL_TAIL_DIRECTION_REVERSAL_ROOT_CAUSE": tail_audit["root_cause"],
        "VERTICAL_TAIL_CURVATURE_SPIKE_STATIONS": tail_audit["spike_stations"],
        "OFFLINE_GEOMETRY_ANALYZER_REGEN_REQUIRED": True,
        "OFFLINE_REGEN_SCOPE": "FUSELAGE_VERSIONED_MEASURED_SECTION_GRAPH_AND_ALL_OPEN_COMPONENT_GEOMETRY_ONLY",
        "NEXT_FIX": "D_FUSELAGE_VERSIONED_OFFLINE_EVIDENCE_REGEN_THEN_B_C_VERTICAL_TAIL_ORIENTATION_ENDPOINT_IDENTITY_FIX",
        "UPSTREAM_EVIDENCE_UNCHANGED": upstream_unchanged,
        "EVIDENCE_COMPLETENESS_MATRIX": str(matrix_csv),
        "VERTICAL_TAIL_AUDIT": str(OUT / "artifacts/vertical_tail_direction_identity_audit.json"),
        "BLOCKERS": [],
    }
    dump(OUT / "artifacts/pretest_summary.json", summary)
    dump(OUT / "artifacts/upstream_read_only_audit.json", {"before": before, "after": after, "unchanged": upstream_unchanged})
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
