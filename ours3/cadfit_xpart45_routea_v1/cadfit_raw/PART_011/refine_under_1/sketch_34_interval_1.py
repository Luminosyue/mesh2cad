import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.41004, 0.09558, -0.00762), normal=(0.93601, 0.3512, 0.02341), xDir=(0.35129, -0.93627, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.36767, 0.13755)
loop_1 = loop_1.lineTo(0.34963, -0.19222)
loop_1 = loop_1.lineTo(0.35919, -0.17926)
loop_1 = loop_1.threePointArc((0.36011, -0.16127), (0.36039, -0.14398))
loop_1 = loop_1.threePointArc((0.36061, -0.12685), (0.36052, -0.11349))
loop_1 = loop_1.threePointArc((0.36133, -0.08061), (0.3615, -0.05231))
loop_1 = loop_1.lineTo(0.36131, -0.03811)
loop_1 = loop_1.threePointArc((0.36328, -0.00283), (0.36583, 0.0304))
loop_1 = loop_1.threePointArc((0.36751, 0.05799), (0.36798, 0.08125))
loop_1 = loop_1.lineTo(0.3685, 0.09741)
loop_1 = loop_1.lineTo(0.36886, 0.10963)
loop_1 = loop_1.lineTo(0.36785, 0.13334)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_34_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_34_interval_1.stl')