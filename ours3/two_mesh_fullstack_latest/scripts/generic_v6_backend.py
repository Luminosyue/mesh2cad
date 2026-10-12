#!/usr/bin/env python3
"""Generic V6 geometry backend for arbitrary meshes (no aircraft ROLE_CONFIG).

Uses geometry_class from the automatic part graph to pick v6_runtime representations,
executes fresh BReps, and writes candidate manifests compatible with run_fullstack QA.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "two_mesh_fullstack_latest"
V6_RUNTIME = ROOT / "case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py"
V6_RESTORE = ROOT / "v6_geometry_backend_restore"

# geometry_class -> list of (representation, sections, profile_count, tolerance)
GEOMETRY_V6_PROFILES: dict[str, list[tuple[str, int, int, float]]] = {
    "THIN_EXTRUSION": [
        ("GLOBAL_UPPER_LOWER_SKINS", 16, 14, 0.001),
        ("PROFILE_EXTRUSION", 12, 12, 0.001),
    ],
    "AXIAL_REVOLUTION_OR_SWEEP": [
        ("PERIODIC_GLOBAL_BSPLINE", 18, 16, 0.001),
        ("SWEEP", 16, 14, 0.001),
    ],
    "MULTI_FEATURE": [
        ("SUBFEATURE_LOFT_UNION", 14, 12, 0.001),
        ("HYBRID_ANALYTIC_FREEFORM", 16, 14, 0.001),
    ],
    "VOLUMETRIC_FREEFORM": [
        ("SEMANTIC_FREEFORM_SKINS", 16, 14, 0.001),
        ("CLOSED_GLOBAL_LOFT", 14, 12, 0.001),
    ],
    "GLOBAL_LOFT_OR_FREEFORM": [
        ("GLOBAL_LOFT", 14, 12, 0.001),
        ("SEMANTIC_FREEFORM_SKINS", 16, 14, 0.001),
    ],
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _runtime():
    spec = importlib.util.spec_from_file_location("generic_v6_runtime", V6_RUNTIME)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _safety():
    sys.path.insert(0, str(V6_RESTORE))
    from backends.v6_backend_safety_wrapper import reload_shape, verify

    return reload_shape, verify


def profiles_for_node(node: dict) -> list[tuple[str, int, int, float]]:
    gclass = node.get("geometry_class") or "GLOBAL_LOFT_OR_FREEFORM"
    return GEOMETRY_V6_PROFILES.get(gclass, GEOMETRY_V6_PROFILES["GLOBAL_LOFT_OR_FREEFORM"])


def generate_part(case_id: str, node: dict) -> list[dict]:
    pid = node["part_id"]
    source_mesh = Path(node["source_part_mesh"])
    base = OUT / "08_multi_candidate_mac" / case_id / pid
    runtime = _runtime()
    reload_shape, verify = _safety()
    source = trimesh.load(source_mesh, force="mesh", process=False)
    rows = []
    for index, (representation, sections, profiles, tolerance) in enumerate(profiles_for_node(node), 1):
        directory = base / f"V6_BACKEND_{index:02d}_{representation}"
        step = directory / "candidate.step"
        manifest_path = directory / "candidate_manifest.json"
        if manifest_path.is_file():
            existing = _load(manifest_path)
            if existing.get("program_executed") and Path(existing["step"]).is_file():
                rows.append(existing)
                continue
        directory.mkdir(parents=True, exist_ok=True)
        error = None
        exit_code = 0
        safety = {}
        try:
            runtime.build_candidate(str(source_mesh), representation, str(step), sections, profiles, tolerance)
            reloaded = reload_shape(step)
            safety = verify(source, reloaded, {})
            if not step.is_file():
                raise RuntimeError("STEP_NOT_WRITTEN")
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            exit_code = 1
        program = directory / "generated_v6_backend.py"
        program.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    f"# generic v6 backend: {representation}",
                    f"# source: {source_mesh}",
                    f"# sections={sections} profiles={profiles} tolerance={tolerance}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        row = {
            "candidate_id": directory.name,
            "case_id": case_id,
            "part_id": pid,
            "hypothesis": {
                "hypothesis_id": f"V6B{index}",
                "representation": representation,
                "sampling_topology_is_constraint_only": True,
            },
            "program": str(program),
            "generated_code_sha256": _sha(program),
            "step": str(step),
            "execution_exit_code": exit_code,
            "program_executed": exit_code == 0 and step.is_file(),
            "step_exists": step.is_file(),
            "candidate_source": "V6_GEOMETRY_BACKEND_GENERIC",
            "geometry_class": node.get("geometry_class"),
            "v6_runtime_config": {
                "representation": representation,
                "sections": sections,
                "profile_count": profiles,
                "tolerance": tolerance,
            },
            "v6_backend_safety": safety,
            "v6_backend_safety_pass": bool(safety.get("safety_pass")),
            "source_mesh_read_count": 1 if exit_code == 0 else 0,
            "historical_step_reused": False,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "backend_error": error,
        }
        _dump(manifest_path, row)
        _dump(directory / "v6_backend_provenance.json", row)
        rows.append(row)
        print(case_id, pid, directory.name, exit_code, step.is_file(), flush=True)
    summary = {
        "case_id": case_id,
        "part_id": pid,
        "geometry_class": node.get("geometry_class"),
        "V6_BACKEND_ATTEMPTED": True,
        "candidates": rows,
    }
    _dump(base / "v6_backend_part_summary.json", summary)
    return rows


def stage_v6_backend(case_id: str | None = None) -> list[dict]:
    summaries = []
    for graph_path in sorted((OUT / "02_cad_part_graph").glob("CASE_*/cad_part_graph.json")):
        graph = _load(graph_path)
        cid = graph["case_id"]
        if case_id and cid != case_id:
            continue
        part_rows = []
        for node in graph["nodes"]:
            part_rows.extend(generate_part(cid, node))
        summaries.append({"case_id": cid, "v6_backend_candidates": len(part_rows)})
    return summaries


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--case")
    args = parser.parse_args()
    print(json.dumps(stage_v6_backend(args.case), indent=2))
