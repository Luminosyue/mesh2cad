import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06458, -0.2325, 0.00993), normal=(0.55682, -0.83063, 0.00124), xDir=(-0.83063, -0.55682, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.58081, 0.55074)
loop_1 = loop_1.threePointArc((-0.58094, 0.49394), (-0.58101, 0.43942))
loop_1 = loop_1.lineTo(-0.58772, 0.45498)
loop_1 = loop_1.lineTo(-0.60087, 0.47339)
loop_1 = loop_1.lineTo(-0.60665, 0.48582)
loop_1 = loop_1.lineTo(-0.60624, 0.49684)
loop_1 = loop_1.lineTo(-0.60279, 0.51235)
loop_1 = loop_1.threePointArc((-0.59481, 0.52492), (-0.58714, 0.53694))
loop_1 = loop_1.lineTo(-0.58143, 0.54944)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_35_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_35_interval_1.stl')