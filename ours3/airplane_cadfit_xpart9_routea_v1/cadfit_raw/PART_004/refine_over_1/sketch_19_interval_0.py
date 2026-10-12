import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.53599, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00734, -0.04356)
loop_1 = loop_1.lineTo(0.94, -0.04608)
loop_1 = loop_1.lineTo(0.94, -0.06416)
loop_1 = loop_1.threePointArc((0.81416, -0.06407), (0.6838, -0.06122))
loop_1 = loop_1.threePointArc((0.57159, -0.05901), (0.45539, -0.05533))
loop_1 = loop_1.threePointArc((0.28909, -0.05236), (0.11659, -0.04676))
loop_1 = loop_1.lineTo(-0.00656, -0.04358)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.75)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_19_interval_0.stl')