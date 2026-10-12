from pathlib import Path
import hashlib

from v13_transform_restore_and_xcaf_assembly.assembly.assembly_quality_audit import (
    count_pcurves_and_trimmed_faces,
    shared_occ_edge_count,
)
from v13_transform_restore_and_xcaf_assembly.assembly.placement_validator import shape_counts
from v13_transform_restore_and_xcaf_assembly.assembly.xcaf_assembly_builder import load_step_shape

paths = [
    "/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router/cases/CASE09/parts/CADPART_005/selected/generated.step",
    "/data/home/cuiyuehan/project/mesh2cad/ours3/v7b_profile_type_aware_open_shell_reconstruction/06_candidates/CADPART_005/PRIMARY/candidate.step",
    "/data/home/cuiyuehan/project/mesh2cad/ours3/v7d3_vertical_tail_geometry_preserving_refit/06_candidates/CADPART_005/v7d3_vertical_tail_local_refit.step",
    "/data/home/cuiyuehan/project/mesh2cad/ours3/v7d3_vertical_tail_geometry_preserving_refit/07_topology/CADPART_005/v7d3_shared_topology_faces.step",
    "/data/home/cuiyuehan/project/mesh2cad/ours3/v7d_common_boundary_control_net/06_candidates/CADPART_005/v7d_constrained_faces.step",
    "/data/home/cuiyuehan/project/mesh2cad/ours3/v7d_common_boundary_control_net/07_v7c_rerun/CADPART_005/v7c_shared_topology_faces.step",
    "/data/home/cuiyuehan/project/mesh2cad/ours3/v11b_real_qwen_mac_open_shell_closure/cases/CASE09/CADPART_005/GEOMETRY_ALTERNATIVE_1_fresh.step",
]

for raw in paths:
    path = Path(raw)
    if not path.exists():
        print("MISSING", raw)
        continue
    shape = load_step_shape(path)
    print(
        path.name,
        hashlib.sha256(path.read_bytes()).hexdigest(),
        shape_counts(shape),
        "shared",
        shared_occ_edge_count(shape),
        "pcurves_trimmed",
        count_pcurves_and_trimmed_faces(shape),
    )
