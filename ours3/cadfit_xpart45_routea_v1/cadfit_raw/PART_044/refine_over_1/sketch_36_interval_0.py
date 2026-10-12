import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.013, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.70333, 0.59993)
loop_1 = loop_1.threePointArc((-0.70162, 0.60808), (-0.70034, 0.61598))
loop_1 = loop_1.threePointArc((-0.69752, 0.63707), (-0.69408, 0.6587))
loop_1 = loop_1.lineTo(-0.68854, 0.69408)
loop_1 = loop_1.threePointArc((-0.68692, 0.70236), (-0.68581, 0.71014))
loop_1 = loop_1.threePointArc((-0.68257, 0.7272), (-0.67886, 0.74464))
loop_1 = loop_1.threePointArc((-0.67626, 0.75919), (-0.67272, 0.7739))
loop_1 = loop_1.threePointArc((-0.67113, 0.78137), (-0.66989, 0.78836))
loop_1 = loop_1.threePointArc((-0.66426, 0.81797), (-0.66211, 0.84))
loop_1 = loop_1.lineTo(-0.72275, 0.83975)
loop_1 = loop_1.lineTo(-0.72222, 0.50397)
loop_1 = loop_1.lineTo(-0.71671, 0.54167)
loop_1 = loop_1.lineTo(-0.706, 0.58571)
loop_1 = loop_1.threePointArc((-0.70455, 0.59294), (-0.70332, 0.59967))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_36_interval_0.stl')