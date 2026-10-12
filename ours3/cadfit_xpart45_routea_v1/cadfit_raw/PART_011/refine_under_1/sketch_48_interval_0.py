import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00738, -0.03777, 0.29585), normal=(0.00929, 0.04277, -0.99904), xDir=(0.0, -0.99908, -0.04277))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0298, -0.38528)
loop_1 = loop_1.lineTo(0.03229, -0.42147)
loop_1 = loop_1.lineTo(0.02978, -0.44286)
loop_1 = loop_1.lineTo(0.01128, -0.45873)
loop_1 = loop_1.threePointArc((0.00097, -0.44573), (-0.00844, -0.43355))
loop_1 = loop_1.lineTo(-0.01786, -0.42147)
loop_1 = loop_1.lineTo(-0.05374, -0.37336)
loop_1 = loop_1.lineTo(-0.06054, -0.36025)
loop_1 = loop_1.lineTo(0.02301, -0.44024)
loop_1 = loop_1.lineTo(0.02729, -0.38716)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_48_interval_0.stl')