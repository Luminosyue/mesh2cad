import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.4401, 0.17523, -0.5178), normal=(-0.54863, -0.81782, -0.17372), xDir=(-0.83044, 0.5571, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08083, -0.34385)
loop_1 = loop_1.threePointArc((-0.07294, -0.36147), (-0.06517, -0.37831))
loop_1 = loop_1.lineTo(-0.06102, -0.3929)
loop_1 = loop_1.lineTo(-0.05886, -0.40369)
loop_1 = loop_1.lineTo(-0.05554, -0.42085)
loop_1 = loop_1.lineTo(-0.05184, -0.45107)
loop_1 = loop_1.lineTo(-0.04771, -0.47851)
loop_1 = loop_1.threePointArc((-0.04488, -0.50151), (-0.04217, -0.5207))
loop_1 = loop_1.threePointArc((-0.03917, -0.54463), (-0.03633, -0.56485))
loop_1 = loop_1.lineTo(-0.03326, -0.58328)
loop_1 = loop_1.lineTo(-0.03195, -0.60048)
loop_1 = loop_1.lineTo(-0.08094, -0.60004)
loop_1 = loop_1.lineTo(-0.08081, -0.34446)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.27)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_7_interval_0.stl')