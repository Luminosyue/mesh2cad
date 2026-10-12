import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh
from OCP.BRepCheck import BRepCheck_Analyzer


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V1 = ROOT / "case09_aircraft_end2end_cad_v1"
MODULE_PATH = V1 / "scripts/end2end_pipeline.py"


def main():
    spec = importlib.util.spec_from_file_location("v1_pipeline", MODULE_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    source = trimesh.load(m.SOURCE, force="mesh", process=False)
    labels = np.load(m.P3 / "triangle_part_id.npy")
    boundary, sharp = m.source_feature_points(source, labels)
    diag = float(np.linalg.norm(source.extents))
    static = {}
    for part_id in ("CADPART_005", "CADPART_006", "CADPART_007"):
        ok, roots, shape = m.read_step(V1 / "05_backend_recovery" / part_id / "reconstructed.step")
        if not (ok and roots and shape and BRepCheck_Analyzer(shape).IsValid()):
            raise RuntimeError(f"invalid static part {part_id}")
        static[part_id] = shape
    results = []
    for fuselage_profiles in (8, 10, 12):
        fuselage_mesh, _ = m.source_part_mesh(source, labels, [8])
        fuselage, _ = m.measured_profile_loft(fuselage_mesh, "Y", 14, fuselage_profiles, "PROBE_FUSELAGE")
        for wing_profiles in (6, 8, 10, 12):
            shapes = [fuselage]
            for part in m.PART_SPECS[1:5]:
                mesh, _ = m.source_part_mesh(source, labels, part["segments"])
                shape, _ = m.measured_profile_loft(mesh, "X", 7, wing_profiles, "PROBE_" + part["part_id"])
                shapes.append(shape)
            shapes.extend(static.values())
            assembly = m.compound(shapes)
            vertices, faces, _ = m.tessellate(assembly)
            mesh = trimesh.Trimesh(vertices, faces, process=False)
            metrics = m.geometry_metrics(source, mesh, diag, samples=30000)
            edges, records = m.true_edges(assembly, diag)
            strip = m.strip_audit(records, diag)
            row = {
                "fuselage_profiles": fuselage_profiles,
                "wing_tail_profiles": wing_profiles,
                "faces": m.topology_count(assembly, m.TopAbs_FACE),
                "edges": m.topology_count(assembly, m.TopAbs_EDGE),
                "sharp_edge_recall": m.recall(sharp, records, diag),
                "feature_boundary_recall": m.recall(boundary, records, diag),
                "strip_edge_count": strip["STRIP_EDGE_COUNT"],
                **metrics,
            }
            results.append(row)
            print(json.dumps(row), flush=True)
    print("BEST=" + json.dumps(sorted(results, key=lambda x: (-x["sharp_edge_recall"], x["CHAMFER"], x["faces"]))[:5]))


if __name__ == "__main__":
    main()
