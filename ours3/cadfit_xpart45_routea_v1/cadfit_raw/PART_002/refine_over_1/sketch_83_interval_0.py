import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.22627, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.25, 0.89164)
loop_1 = loop_1.lineTo(-0.2497, 0.85344)
loop_1 = loop_1.threePointArc((-0.24052, 0.85839), (-0.23102, 0.8633))
loop_1 = loop_1.lineTo(-0.1907, 0.87399)
loop_1 = loop_1.lineTo(-0.15421, 0.88141)
loop_1 = loop_1.lineTo(-0.11748, 0.88586)
loop_1 = loop_1.lineTo(-0.07967, 0.88874)
loop_1 = loop_1.threePointArc((-0.05147, 0.89022), (-0.02225, 0.89151))
loop_1 = loop_1.lineTo(-0.24983, 0.89164)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_83_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_83_interval_0.stl')