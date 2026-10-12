import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.25564, -0.0343, -0.007), normal=(-0.16313, -0.08791, -0.98268), xDir=(0.0, -0.99602, 0.0891))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04317, 0.38059)
loop_1 = loop_1.lineTo(-0.04817, 0.40827)
loop_1 = loop_1.threePointArc((-0.05356, 0.43529), (-0.0575, 0.45408))
loop_1 = loop_1.lineTo(-0.05934, 0.46747)
loop_1 = loop_1.lineTo(-0.06353, 0.48353)
loop_1 = loop_1.threePointArc((-0.06497, 0.49545), (-0.06674, 0.50302))
loop_1 = loop_1.lineTo(-0.1031, 0.50147)
loop_1 = loop_1.lineTo(-0.01904, -0.49095)
loop_1 = loop_1.lineTo(-0.00113, 0.10931)
loop_1 = loop_1.lineTo(-0.01034, 0.09921)
loop_1 = loop_1.lineTo(-0.01968, 0.2888)
loop_1 = loop_1.threePointArc((-0.02609, 0.31364), (-0.03461, 0.34917))
loop_1 = loop_1.lineTo(-0.04289, 0.37934)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_6_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_6_interval_1.stl')