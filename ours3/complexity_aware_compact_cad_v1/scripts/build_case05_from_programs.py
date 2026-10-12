#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

from OCP.BRep import BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.TopoDS import TopoDS_Compound
from OCP.gp import gp_Trsf


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "complexity_aware_compact_cad_v1/case05"

COMPONENTS = [
    ("CADPART_000", ROOT / "batch_real_mesh2cad_v1/cases/CASE_05/cad_recovery/CADPART_000/candidate_B_loft/deterministic_program.py", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_000/accepted/local_to_global_transform.json"),
    ("CADPART_001", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_001/candidate_L/deterministic_program.py", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_001/local_to_global_transform.json"),
    ("CADPART_002", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_002/candidate_L/deterministic_program.py", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_002/local_to_global_transform.json"),
    ("CADPART_004", ROOT / "batch_real_mesh2cad_v1/cases/CASE_05/cad_recovery/CADPART_004/candidate_B_loft/deterministic_program.py", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_004/accepted/local_to_global_transform.json"),
    ("CADPART_005", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_005/candidate_L/deterministic_program.py", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_005/local_to_global_transform.json"),
    ("CADPART_006", ROOT / "batch_real_mesh2cad_v1/cases/CASE_05/cad_recovery/CADPART_006/candidate_B_loft/deterministic_program.py", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_006/accepted/local_to_global_transform.json"),
    ("CADPART_007", ROOT / "batch_real_mesh2cad_v1/cases/CASE_05/cad_recovery/CADPART_007/candidate_B_loft/deterministic_program.py", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_007/accepted/local_to_global_transform.json"),
    ("CADPART_008", ROOT / "batch_real_mesh2cad_v1/cases/CASE_05/cad_recovery/CADPART_008/candidate_B_loft/deterministic_program.py", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_008/accepted/local_to_global_transform.json"),
    ("CADPART_009", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_009/candidate_L/deterministic_program.py", ROOT / "best_multipart_full_recovery_v2/parts/CADPART_009/local_to_global_transform.json"),
    ("CADPART_003_SUBPART_00", ROOT / "case05_residual_part003_recovery_v3/parts/CADPART_003/subparts_b2/SUBPART_00/candidate_loft/deterministic_program.py", ROOT / "case05_residual_part003_recovery_v3/parts/CADPART_003/subparts_b2/SUBPART_00/local_to_global_transform.json"),
]


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transform(shape, matrix):
    matrix = np.asarray(matrix, dtype=float)
    trsf = gp_Trsf()
    trsf.SetValues(*matrix[:3, :4].reshape(-1).tolist())
    operation = BRepBuilderAPI_Transform(shape, trsf, True)
    operation.Build()
    if not operation.IsDone() or operation.Shape().IsNull():
        raise RuntimeError("component transform failed")
    return operation.Shape()


def write_step(shape, path):
    writer = STEPControl_Writer(); writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP write failed: {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-sections", type=int, default=0, help="0 selects full-section smooth global refit")
    parser.add_argument("--mode", default="program_provenance")
    args = parser.parse_args()
    component_dir = OUT / "components"; component_dir.mkdir(parents=True, exist_ok=True)
    shapes = []; records = []
    for index, (part_id, program, ledger_path) in enumerate(COMPONENTS):
        module = load_module(f"compact_{index}", program)
        if not hasattr(module, "RULED") or not hasattr(module, "SECTIONS"):
            raise RuntimeError(f"missing ruled/sections contract: {program}")
        original_section_count = len(module.SECTIONS)
        if args.target_sections:
            keep = np.unique(np.rint(np.linspace(0, original_section_count - 1, args.target_sections)).astype(int))
            module.SECTIONS = [module.SECTIONS[int(i)] for i in keep]
            module.RULED = True
        else:
            module.RULED = False
        local_step = component_dir / f"{part_id}_{args.mode}_local.step"
        module.OUTPUT = local_step
        local_shape = module.build()
        if not BRepCheck_Analyzer(local_shape).IsValid():
            raise RuntimeError(f"local compact BRep invalid: {part_id}")
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        if not ledger.get("roundtrip_pass") or ledger.get("ICP_USED"):
            raise RuntimeError(f"invalid frozen transform: {part_id}")
        placed = transform(local_shape, ledger["CANONICAL_TO_SOURCE"])
        if not BRepCheck_Analyzer(placed).IsValid():
            raise RuntimeError(f"placed compact BRep invalid: {part_id}")
        placed_step = component_dir / f"{part_id}_{args.mode}_source_frame.step"
        write_step(placed, placed_step)
        shapes.append(placed)
        records.append({
            "component_id": part_id,
            "program": str(program),
            "program_sha256": sha256(program),
            "sections_original": original_section_count,
            "sections_candidate": len(module.SECTIONS),
            "points_per_section": len(module.SECTIONS[0]["points"]),
            "rule_original": True,
            "rule_candidate": bool(module.RULED),
            "transform_ledger": str(ledger_path),
            "transform": "CANONICAL_TO_SOURCE",
            "local_step": str(local_step),
            "placed_step": str(placed_step),
        })
        print(f"COMPONENT_DONE={part_id} SECTIONS={len(module.SECTIONS)} RULED={module.RULED}", flush=True)
    compound = TopoDS_Compound(); builder = BRep_Builder(); builder.MakeCompound(compound)
    for shape in shapes:
        builder.Add(compound, shape)
    if not BRepCheck_Analyzer(compound).IsValid():
        raise RuntimeError("compact assembly BRep invalid")
    output = OUT / f"candidates/compact_{args.mode}.step"
    output.parent.mkdir(parents=True, exist_ok=True); write_step(compound, output)
    metadata = {
        "output": str(output),
        "component_count": len(records),
        "components": records,
        "method": "ORIGINAL_MEASURED_SECTIONS_WITH_FROZEN_COMPONENT_TRANSFORMS",
        "target_sections": args.target_sections,
        "mode": args.mode,
        "unrestricted_icp_used": False,
        "triangulated_mesh_output": False,
    }
    (OUT / f"candidates/{args.mode}_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
