import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.40517), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11319, -0.85791)
loop_1 = loop_1.lineTo(-0.02015, -0.85747)
loop_1 = loop_1.lineTo(-0.02061, -0.5914)
loop_1 = loop_1.lineTo(-0.02704, -0.63447)
loop_1 = loop_1.lineTo(-0.03443, -0.67046)
loop_1 = loop_1.lineTo(-0.04872, -0.74769)
loop_1 = loop_1.threePointArc((-0.05186, -0.76158), (-0.05526, -0.77577))
loop_1 = loop_1.lineTo(-0.065, -0.8066)
loop_1 = loop_1.lineTo(-0.0788, -0.83273)
loop_1 = loop_1.threePointArc((-0.09747, -0.84934), (-0.11303, -0.85776))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_56_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_56_interval_0.stl')