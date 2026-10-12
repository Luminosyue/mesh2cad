import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.97236, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0347, 7e-05)
loop_1 = loop_1.lineTo(0.03429, -0.17)
loop_1 = loop_1.lineTo(-0.02548, -0.16975)
loop_1 = loop_1.threePointArc((-0.01857, -0.15448), (-0.01215, -0.13988))
loop_1 = loop_1.lineTo(0.00032, -0.10528)
loop_1 = loop_1.lineTo(0.02136, -0.03699)
loop_1 = loop_1.lineTo(0.03303, -0.00416)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_28_interval_0.stl')