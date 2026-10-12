#!/usr/bin/env python3
"""Assemble the 45 existing faceted component STEPs into one XCAF STEP.

Does not rebuild P3, Point2CAD, or per-component faceted STEPs.
Does not run a native STEPCAF reload of the 1.8 GiB result.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path


PROJECT = Path("/data/home/cuiyuehan/project/mesh2cad")
V13 = PROJECT / "ours3/v13_transform_restore_and_xcaf_assembly"
ROOT = PROJECT / "ours3/tank_p3_component_fullstack_multibackend_v2"
COMPONENTS = ROOT / "03_components"
OUTPUT = ROOT / "07_assembly/tank_p3_dynamic_component_assembly.step"
MANIFEST = ROOT / "artifacts/tank_p3_dynamic_component_assembly_manifest.json"
EXPECTED = 45


def load_entries() -> list[dict]:
    entries = []
    for index in range(EXPECTED):
        component_id = f"P3_COMPONENT_{index:03d}"
        selected = json.loads(
            (COMPONENTS / component_id / "selected/selected_manifest.json").read_text()
        )
        step = Path(selected["step_path"])
        if not step.is_file() or step.stat().st_size == 0:
            raise FileNotFoundError(component_id)
        entries.append(
            {
                "part_id": component_id,
                "semantic_role": component_id,
                "builder": selected.get("selected_backend", "FACETED_FALLBACK"),
                "route_status": "SELECTED",
                "quality_tag": selected.get("representation", "MESH_DERIVED_FACETED_BREP"),
                "geometry_present": True,
                "fresh_step_path": str(step),
                "T_part_local_to_source_global": selected["local_to_global_transform"],
                "triangle_count": int(selected.get("triangle_count", 0)),
                "step_size_bytes": int(step.stat().st_size),
            }
        )
    return entries


def text_qa(path: Path, names: list[str]) -> dict:
    found = {name: False for name in names}
    remaining = set(names)
    with path.open("rb") as handle:
        for raw in handle:
            if not remaining:
                break
            line = raw.decode("latin1", errors="ignore")
            hit = [name for name in remaining if name in line]
            for name in hit:
                found[name] = True
                remaining.remove(name)
    return {
        "component_labels_verified": all(found.values()),
        "missing_component_labels": sorted(remaining),
        "checked_component_count": len(names),
        "validation_mode": "NONDESTRUCTIVE_STEP_TEXT",
        "native_stepcaf_reload_completed": False,
    }


def main() -> int:
    sys.path.insert(0, str(V13))
    from OCP.TopLoc import TopLoc_Location
    from OCP.XCAFDoc import XCAFDoc_DocumentTool
    from assembly.xcaf_assembly_builder import (
        _new_document,
        _set_name,
        _trsf_from_matrix,
        _without_location,
        export_xcaf_step,
        load_step_shape,
    )

    started = time.time()
    entries = load_entries()
    print(f"loaded {len(entries)} component manifests", flush=True)
    doc = _new_document()
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    root = shape_tool.NewShape()
    _set_name(root, "TANK_P3_DYNAMIC_COMPONENT_ASSEMBLY_ROOT")
    components = []
    for index, entry in enumerate(entries, start=1):
        size_mb = entry["step_size_bytes"] / (1024 * 1024)
        print(
            f"[{index}/{EXPECTED}] reading {entry['part_id']} "
            f"({size_mb:.1f} MiB, {entry['triangle_count']} faces)",
            flush=True,
        )
        part_started = time.time()
        local_shape = load_step_shape(entry["fresh_step_path"])
        definition = shape_tool.AddShape(_without_location(local_shape), False)
        _set_name(
            definition,
            f"{entry['part_id']}__{entry['semantic_role']}__{entry['builder']}__{entry['route_status']}",
        )
        trsf = _trsf_from_matrix(entry["T_part_local_to_source_global"])
        component = shape_tool.AddComponent(root, definition, TopLoc_Location(trsf))
        _set_name(component, f"{entry['part_id']}__{entry['semantic_role']}__{entry['quality_tag']}")
        components.append(entry["part_id"])
        print(
            f"[{index}/{EXPECTED}] added {entry['part_id']} in {time.time() - part_started:.1f}s",
            flush=True,
        )
    shape_tool.UpdateAssemblies()
    print("writing XCAF STEP (no reload)", flush=True)
    write_started = time.time()
    export_xcaf_step(doc, OUTPUT, "TANK_P3_DYNAMIC_COMPONENT_FULLSTACK")
    write_seconds = round(time.time() - write_started, 3)
    print(f"write done in {write_seconds:.1f}s size={OUTPUT.stat().st_size}", flush=True)
    qa = text_qa(OUTPUT, [entry["part_id"] for entry in entries])
    qa.update(
        {
            "step_path": str(OUTPUT),
            "step_size_bytes": int(OUTPUT.stat().st_size),
            "component_count": len(components),
            "expected_component_count": EXPECTED,
            "write_seconds": write_seconds,
            "total_seconds": round(time.time() - started, 3),
        }
    )
    manifest = {
        "schema": "TANK_P3_DYNAMIC_COMPONENT_ASSEMBLY_V2",
        "assembly_type": "XCAF_INDEPENDENT_COMPONENT_ASSEMBLY",
        "independent_parts": True,
        "boolean_fused": False,
        "representation": "MESH_DERIVED_FACETED_BREP",
        "source_components": [entry["fresh_step_path"] for entry in entries],
        "component_names": components,
        "step_path": str(OUTPUT),
        "reload_qa": qa,
        "honest_note": (
            "XCAF assembly of the 45 existing faceted_fallback STEP files. "
            "Native STEPCAF reload was skipped to avoid the previous 1.8 GiB hang."
        ),
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(qa, indent=2), flush=True)
    if not qa["component_labels_verified"] or len(components) != EXPECTED:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
