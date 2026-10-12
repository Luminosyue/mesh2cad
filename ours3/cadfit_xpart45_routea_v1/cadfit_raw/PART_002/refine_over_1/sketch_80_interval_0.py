import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.19373, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.42492, -0.49963)
loop_1 = loop_1.lineTo(0.42406, -0.81)
loop_1 = loop_1.lineTo(0.26, -0.80943)
loop_1 = loop_1.lineTo(0.26048, -0.72509)
loop_1 = loop_1.threePointArc((0.2906, -0.70675), (0.31914, -0.68904))
loop_1 = loop_1.threePointArc((0.32644, -0.6846), (0.3328, -0.67987))
loop_1 = loop_1.lineTo(0.36309, -0.65793)
loop_1 = loop_1.lineTo(0.39603, -0.61689)
loop_1 = loop_1.threePointArc((0.40078, -0.6024), (0.40478, -0.58862))
loop_1 = loop_1.lineTo(0.40774, -0.57849)
loop_1 = loop_1.threePointArc((0.41116, -0.55938), (0.41505, -0.53953))
loop_1 = loop_1.threePointArc((0.41897, -0.52261), (0.42318, -0.50532))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_80_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_80_interval_0.stl')