import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.79741, -0.35746, -0.03782), normal=(0.93601, 0.3512, 0.02341), xDir=(0.35129, -0.93627, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29559, -0.21112)
loop_1 = loop_1.lineTo(-0.31025, 0.199)
loop_1 = loop_1.lineTo(0.28916, 0.199)
loop_1 = loop_1.lineTo(0.30468, -0.21112)
loop_1 = loop_1.lineTo(-0.28385, -0.21112)
loop_1 = loop_1.lineTo(-0.29559, -0.21112)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_3_interval_0.stl')