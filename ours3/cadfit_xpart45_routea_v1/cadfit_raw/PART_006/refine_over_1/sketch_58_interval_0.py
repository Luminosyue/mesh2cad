import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.99909, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.13376, -0.41644)
loop_1 = loop_1.threePointArc((0.14768, -0.41661), (0.16217, -0.41716))
loop_1 = loop_1.lineTo(0.17621, -0.41645)
loop_1 = loop_1.lineTo(0.40021, -0.41587)
loop_1 = loop_1.lineTo(0.38317, -0.40385)
loop_1 = loop_1.threePointArc((0.32027, -0.40213), (0.26366, -0.40647))
loop_1 = loop_1.lineTo(0.13395, -0.41644)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_58_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_58_interval_0.stl')