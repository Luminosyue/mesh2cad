import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0211, -0.2548, 0.07941), normal=(0.96453, 0.26357, -0.0143), xDir=(0.2636, -0.96463, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23371, 0.63424)
loop_1 = loop_1.lineTo(0.23577, 0.10745)
loop_1 = loop_1.lineTo(0.20938, 0.11803)
loop_1 = loop_1.lineTo(0.1172, 0.17117)
loop_1 = loop_1.lineTo(0.09941, 0.1888)
loop_1 = loop_1.lineTo(0.08456, 0.20563)
loop_1 = loop_1.lineTo(0.07143, 0.22317)
loop_1 = loop_1.lineTo(0.07786, 0.36616)
loop_1 = loop_1.lineTo(0.07486, 0.42102)
loop_1 = loop_1.lineTo(0.07666, 0.47589)
loop_1 = loop_1.lineTo(0.08325, 0.53076)
loop_1 = loop_1.lineTo(0.11252, 0.58922)
loop_1 = loop_1.lineTo(0.21141, 0.62547)
loop_1 = loop_1.lineTo(0.2276, 0.63215)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_50_interval_0.stl')