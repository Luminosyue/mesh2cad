import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.41761, -0.8492, 0.04071), normal=(0.41044, 0.91189, 0.00105), xDir=(0.91189, -0.41044, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34025, 0.56287)
loop_1 = loop_1.lineTo(0.30194, 0.56287)
loop_1 = loop_1.lineTo(0.31645, 0.53933)
loop_1 = loop_1.lineTo(0.3338, 0.50816)
loop_1 = loop_1.lineTo(0.34046, 0.47484)
loop_1 = loop_1.lineTo(0.34026, 0.5617)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_6_interval_0.stl')