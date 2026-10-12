import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.00992, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.94, 0.01834)
loop_1 = loop_1.lineTo(-0.9394, -0.03727)
loop_1 = loop_1.lineTo(-0.91705, -0.03512)
loop_1 = loop_1.lineTo(-0.86343, -0.03489)
loop_1 = loop_1.threePointArc((-0.77477, -0.03047), (-0.69031, -0.02553))
loop_1 = loop_1.lineTo(-0.52592, -0.01577)
loop_1 = loop_1.lineTo(-0.00656, 0.01834)
loop_1 = loop_1.lineTo(-0.93935, 0.01834)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.57)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_66_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_66_interval_0.stl')