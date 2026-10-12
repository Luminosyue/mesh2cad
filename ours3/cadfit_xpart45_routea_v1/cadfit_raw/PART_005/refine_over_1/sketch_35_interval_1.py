import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02764, -0.06823, -0.11884), normal=(0.77402, -0.63316, 0.00043), xDir=(-0.63316, -0.77402, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29869, 0.40021)
loop_1 = loop_1.lineTo(-0.23495, 0.47398)
loop_1 = loop_1.lineTo(-0.18803, 0.47374)
loop_1 = loop_1.lineTo(-0.18804, 0.4482)
loop_1 = loop_1.lineTo(-0.23826, 0.432)
loop_1 = loop_1.lineTo(-0.25657, 0.42198)
loop_1 = loop_1.lineTo(-0.27508, 0.41045)
loop_1 = loop_1.lineTo(-0.29738, 0.40078)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.96)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_35_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_35_interval_1.stl')