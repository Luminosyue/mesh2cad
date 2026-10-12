from pathlib import Path

from v13_transform_restore_and_xcaf_assembly.assembly.assembly_quality_audit import topology_audit
from v13_transform_restore_and_xcaf_assembly.assembly.transform_restore import restore_transform
from v13_transform_restore_and_xcaf_assembly.assembly.xcaf_assembly_builder import (
    build_xcaf_assembly,
    export_xcaf_step,
    load_step_shape,
)


STEP = Path(
    "/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router/"
    "cases/CASE09/parts/CADPART_001/selected/generated.step"
)

assert restore_transform(
    "P",
    {"local_to_global_transform": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]},
).determinant == 1.0
shape = load_step_shape(STEP)
print("SHAPE_TYPE", shape.ShapeType())
print("TOPOLOGY", topology_audit(shape, shape))
part = {
    "part_id": "P",
    "semantic_role": "TEST",
    "builder": "EXTRUSION",
    "route_status": "SUCCESS_ACCEPTABLE",
    "quality_tag": "ACCEPTABLE",
    "geometry_present": True,
    "fresh_step_path": str(STEP),
    "T_part_local_to_source_global": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
}
built = build_xcaf_assembly("SMOKE", [part])
output = Path("/tmp/v13_smoke.step")
export_xcaf_step(built.doc, output, "SMOKE")
print("XCAF_STEP", output, output.stat().st_size)
