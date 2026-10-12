import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0362, -0.0883, -0.33314), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.42929, 0.88303)
loop_1 = loop_1.threePointArc((-0.45361, 0.87008), (-0.47906, 0.85683))
loop_1 = loop_1.lineTo(-0.51431, 0.83365)
loop_1 = loop_1.lineTo(-0.52886, 0.82262)
loop_1 = loop_1.lineTo(-0.58254, 0.77436)
loop_1 = loop_1.lineTo(-0.62845, 0.73015)
loop_1 = loop_1.lineTo(-0.63862, 0.71918)
loop_1 = loop_1.lineTo(-0.67255, 0.68426)
loop_1 = loop_1.lineTo(-0.68056, 0.67375)
loop_1 = loop_1.lineTo(-0.7101, 0.63097)
loop_1 = loop_1.threePointArc((-0.72222, 0.6125), (-0.73129, 0.59787))
loop_1 = loop_1.lineTo(-0.73985, 0.58467)
loop_1 = loop_1.lineTo(-0.43241, 0.87997)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.8)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_23_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_23_interval_1.stl')