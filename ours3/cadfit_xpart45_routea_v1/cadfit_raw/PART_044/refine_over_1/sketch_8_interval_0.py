import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.48399, 0.1098, -0.5317), normal=(-0.54863, -0.81782, -0.17372), xDir=(-0.83044, 0.5571, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04771, -0.11835)
loop_1 = loop_1.lineTo(-0.03633, -0.11833)
loop_1 = loop_1.lineTo(-0.03399, -0.10792)
loop_1 = loop_1.lineTo(-0.03355, -0.07462)
loop_1 = loop_1.lineTo(-0.02921, -0.06364)
loop_1 = loop_1.lineTo(-0.08072, -0.11427)
loop_1 = loop_1.threePointArc((-0.07106, -0.11743), (-0.06529, -0.11948))
loop_1 = loop_1.lineTo(-0.04771, -0.11835)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_8_interval_0.stl')