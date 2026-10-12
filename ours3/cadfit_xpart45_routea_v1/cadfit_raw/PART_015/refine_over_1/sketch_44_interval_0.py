import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21825), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77134, 0.54792)
loop_1 = loop_1.lineTo(0.77986, 0.53713)
loop_1 = loop_1.lineTo(0.80783, 0.49742)
loop_1 = loop_1.lineTo(0.82573, 0.46912)
loop_1 = loop_1.lineTo(0.82945, 0.54792)
loop_1 = loop_1.lineTo(0.77142, 0.54792)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_44_interval_0.stl')