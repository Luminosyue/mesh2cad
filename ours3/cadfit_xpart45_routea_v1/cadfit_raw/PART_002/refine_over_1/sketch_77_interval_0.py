import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.22041, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.54138, -0.76145)
loop_1 = loop_1.lineTo(0.54794, -0.72819)
loop_1 = loop_1.lineTo(0.55727, -0.7066)
loop_1 = loop_1.lineTo(0.56381, -0.69071)
loop_1 = loop_1.lineTo(0.57118, -0.6762)
loop_1 = loop_1.lineTo(0.57085, -0.81)
loop_1 = loop_1.lineTo(0.52541, -0.80977)
loop_1 = loop_1.lineTo(0.53778, -0.78228)
loop_1 = loop_1.lineTo(0.54103, -0.76326)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_77_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_77_interval_0.stl')