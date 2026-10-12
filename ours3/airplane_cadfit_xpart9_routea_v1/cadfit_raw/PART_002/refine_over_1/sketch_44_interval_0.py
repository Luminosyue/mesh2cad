import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.10039, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.97718, -0.00845)
loop_1 = loop_1.lineTo(0.97661, -0.17)
loop_1 = loop_1.lineTo(0.77609, -0.16953)
loop_1 = loop_1.lineTo(0.8065, -0.15709)
loop_1 = loop_1.threePointArc((0.83886, -0.13992), (0.87262, -0.12261))
loop_1 = loop_1.lineTo(0.89585, -0.10699)
loop_1 = loop_1.threePointArc((0.90681, -0.09866), (0.91841, -0.0906))
loop_1 = loop_1.lineTo(0.94197, -0.07381)
loop_1 = loop_1.lineTo(0.97029, -0.04017)
loop_1 = loop_1.lineTo(0.97327, -0.02876)
loop_1 = loop_1.lineTo(0.97714, -0.00865)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_44_interval_0.stl')