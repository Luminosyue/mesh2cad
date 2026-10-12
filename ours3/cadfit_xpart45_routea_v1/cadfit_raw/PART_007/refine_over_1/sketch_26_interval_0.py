import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.23282, 0.37464, 0.5663), normal=(0.38978, -0.0, -0.92091), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.36464, 0.24229)
loop_1 = loop_1.lineTo(1.36464, 0.08031)
loop_1 = loop_1.lineTo(1.3613, 0.09804)
loop_1 = loop_1.lineTo(1.35451, 0.1282)
loop_1 = loop_1.lineTo(1.34788, 0.1696)
loop_1 = loop_1.threePointArc((1.3438, 0.17999), (1.34063, 0.18863))
loop_1 = loop_1.lineTo(1.32328, 0.21874)
loop_1 = loop_1.lineTo(1.30921, 0.24229)
loop_1 = loop_1.lineTo(1.36275, 0.24229)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.64)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_26_interval_0.stl')