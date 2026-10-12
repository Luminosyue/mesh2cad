import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.01517), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.09346, 0.95942)
loop_1 = loop_1.lineTo(0.06284, 0.93001)
loop_1 = loop_1.threePointArc((0.0414, 0.90741), (0.02568, 0.89159))
loop_1 = loop_1.lineTo(0.02038, 0.97477)
loop_1 = loop_1.lineTo(0.12749, 0.97453)
loop_1 = loop_1.lineTo(0.09356, 0.95947)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_57_interval_0.stl')