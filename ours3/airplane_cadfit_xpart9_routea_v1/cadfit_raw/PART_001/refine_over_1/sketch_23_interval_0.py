import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.98, 0.1327, 0.04863), normal=(-1.0, 0.0, -0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23113, -0.04741)
loop_1 = loop_1.lineTo(0.20618, -0.0566)
loop_1 = loop_1.threePointArc((0.18266, -0.06502), (0.16069, -0.07259))
loop_1 = loop_1.lineTo(0.11407, -0.08849)
loop_1 = loop_1.threePointArc((0.10177, -0.09221), (0.0915, -0.09513))
loop_1 = loop_1.threePointArc((0.06325, -0.1039), (0.03645, -0.11181))
loop_1 = loop_1.lineTo(0.02235, -0.11544)
loop_1 = loop_1.lineTo(0.23113, -0.11745)
loop_1 = loop_1.lineTo(0.23113, -0.05006)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.92)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_23_interval_0.stl')