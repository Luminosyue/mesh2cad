import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V1 = ROOT / "case09_aircraft_end2end_cad_v1"


def main():
    spec = importlib.util.spec_from_file_location("v1", V1 / "scripts/end2end_pipeline.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    source = trimesh.load(m.SOURCE, force="mesh", process=False)
    labels = np.load(m.P3 / "triangle_part_id.npy")
    for part in m.PART_SPECS[1:5]:
        mesh, _ = m.source_part_mesh(source, labels, part["segments"])
        for sections in (7, 10, 14, 20):
            shape, _ = m.measured_profile_loft(mesh, part["axis"], sections, 12, part["part_id"])
            v, f, _ = m.tessellate(shape); cad = trimesh.Trimesh(v, f, process=False)
            q = m.geometry_metrics(mesh, cad, samples=30000)
            print(json.dumps({"part_id": part["part_id"], "sections": sections, "profiles": 12, "Q": m.qclass(q, True), **q}), flush=True)
    for part in m.PART_SPECS[5:]:
        target, _ = m.source_part_mesh(source, labels, part["segments"])
        segment_meshes = [trimesh.load(m.P3 / f"part_{s:03d}.obj", force="mesh", process=False) for s in part["segments"]]
        for sections in (3, 5, 7, 10):
            for profiles in (12, 16):
                shapes = [m.measured_profile_loft(mesh, part["axis"], sections, profiles, part["part_id"])[0] for mesh in segment_meshes]
                shape = m.compound(shapes)
                v, f, _ = m.tessellate(shape); cad = trimesh.Trimesh(v, f, process=False)
                q = m.geometry_metrics(target, cad, samples=30000)
                print(json.dumps({"part_id": part["part_id"], "sections": sections, "profiles": profiles, "Q": m.qclass(q, True), **q}), flush=True)


if __name__ == "__main__":
    main()
