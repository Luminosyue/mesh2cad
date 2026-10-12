import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.25607, 0.83814, -0.04955), normal=(0.32593, -0.94536, 0.0075), xDir=(-0.94539, -0.32594, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1834, -0.22138)
loop_1 = loop_1.lineTo(-0.20007, -0.26253)
loop_1 = loop_1.lineTo(-0.2274, -0.28907)
loop_1 = loop_1.lineTo(-0.24748, -0.29334)
loop_1 = loop_1.lineTo(-0.27311, -0.30237)
loop_1 = loop_1.lineTo(-0.28484, -0.30236)
loop_1 = loop_1.lineTo(-0.30545, -0.30288)
loop_1 = loop_1.lineTo(-0.31878, -0.30244)
loop_1 = loop_1.threePointArc((-0.34206, -0.30072), (-0.36443, -0.29926))
loop_1 = loop_1.lineTo(-0.3833, -0.29743)
loop_1 = loop_1.lineTo(-0.41009, -0.29331)
loop_1 = loop_1.lineTo(-0.42031, -0.2888)
loop_1 = loop_1.lineTo(-0.43844, -0.27889)
loop_1 = loop_1.lineTo(-0.45116, -0.27068)
loop_1 = loop_1.lineTo(-0.46258, -0.26253)
loop_1 = loop_1.lineTo(-0.48902, -0.2267)
loop_1 = loop_1.lineTo(-0.18401, -0.22138)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.52)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_11_interval_0.stl')