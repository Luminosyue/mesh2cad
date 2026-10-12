import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0362, -0.0883, -0.19314), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.8041, -0.51521)
loop_1 = loop_1.lineTo(0.36745, -0.81777)
loop_1 = loop_1.threePointArc((0.31902, -0.84027), (0.27365, -0.85926))
loop_1 = loop_1.threePointArc((0.15766, -0.89105), (0.03885, -0.90685))
loop_1 = loop_1.threePointArc((-0.06311, -0.91191), (-0.1596, -0.89978))
loop_1 = loop_1.lineTo(-0.18986, -0.89631)
loop_1 = loop_1.threePointArc((-0.28198, -0.87539), (-0.36517, -0.84485))
loop_1 = loop_1.threePointArc((-0.49528, -0.78353), (-0.60716, -0.70088))
loop_1 = loop_1.lineTo(-0.62912, -0.68488)
loop_1 = loop_1.threePointArc((-0.67515, -0.65203), (-0.72064, -0.61461))
loop_1 = loop_1.threePointArc((-0.76371, -0.56504), (-0.79977, -0.51925))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.67)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_1_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_1_interval_1.stl')