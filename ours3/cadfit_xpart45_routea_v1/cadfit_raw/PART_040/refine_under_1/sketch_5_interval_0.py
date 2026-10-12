import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.88128, -0.03654, -0.01896), normal=(0.70381, 0.71038, -0.00297), xDir=(0.71039, -0.70381, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.31955, 0.03)
loop_1 = loop_1.lineTo(0.3173, 0.01891)
loop_1 = loop_1.lineTo(0.31745, 0.00217)
loop_1 = loop_1.threePointArc((0.31724, -0.0109), (0.31757, -0.02018))
loop_1 = loop_1.lineTo(0.31848, -0.03452)
loop_1 = loop_1.lineTo(0.31755, -0.04792)
loop_1 = loop_1.lineTo(0.31678, -0.06414)
loop_1 = loop_1.lineTo(0.31524, -0.08217)
loop_1 = loop_1.threePointArc((0.31481, -0.09784), (0.31476, -0.11289))
loop_1 = loop_1.threePointArc((0.31378, -0.12733), (0.31314, -0.13447))
loop_1 = loop_1.lineTo(0.31063, 0.09309)
loop_1 = loop_1.lineTo(0.31955, 0.03)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_5_interval_0.stl')