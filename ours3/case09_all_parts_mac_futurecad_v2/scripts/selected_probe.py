import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V1 = ROOT / "case09_aircraft_end2end_cad_v1"
SECTIONS = {"CADPART_000": 14, "CADPART_001": 20, "CADPART_002": 10, "CADPART_003": 7, "CADPART_004": 10, "CADPART_005": 7, "CADPART_006": 7, "CADPART_007": 7}
PROFILES = {"CADPART_000": 10, **{f"CADPART_{i:03d}": (12 if i < 5 else 16) for i in range(1, 8)}}


def main():
    spec = importlib.util.spec_from_file_location("v1", V1 / "scripts/end2end_pipeline.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    source = trimesh.load(m.SOURCE, force="mesh", process=False)
    labels = np.load(m.P3 / "triangle_part_id.npy")
    shapes = []
    part_rows = []
    for part in m.PART_SPECS:
        target, _ = m.source_part_mesh(source, labels, part["segments"])
        local = []
        for segment in part["segments"]:
            mesh = trimesh.load(m.P3 / f"part_{segment:03d}.obj", force="mesh", process=False)
            shape, _ = m.measured_profile_loft(mesh, part["axis"], SECTIONS[part["part_id"]], PROFILES[part["part_id"]], part["part_id"])
            local.append(shape)
        shape = m.compound(local); shapes.append(shape)
        v, f, _ = m.tessellate(shape); cad = trimesh.Trimesh(v, f, process=False)
        qa = m.geometry_metrics(target, cad, samples=30000)
        part_rows.append({"part_id": part["part_id"], "Q": m.qclass(qa, True), **qa})
    assembly = m.compound(shapes)
    v, f, _ = m.tessellate(assembly); cad = trimesh.Trimesh(v, f, process=False)
    diag = float(np.linalg.norm(source.extents)); qa = m.geometry_metrics(source, cad, diag, samples=50000)
    boundary, sharp = m.source_feature_points(source, labels); _, records = m.true_edges(assembly, diag)
    result = {
        "part_rows": part_rows,
        "faces": m.topology_count(assembly, m.TopAbs_FACE),
        "edges": m.topology_count(assembly, m.TopAbs_EDGE),
        "sharp_edge_recall": m.recall(sharp, records, diag),
        "feature_boundary_recall": m.recall(boundary, records, diag),
        "strip": m.strip_audit(records, diag),
        "GEOM_Q": m.qclass(qa, True),
        **qa,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
