import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.33412, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.37598, 0.77)
loop_1 = loop_1.lineTo(0.33774, 0.7154)
loop_1 = loop_1.lineTo(0.35328, 0.67666)
loop_1 = loop_1.lineTo(0.3651, 0.63792)
loop_1 = loop_1.threePointArc((0.37001, 0.61968), (0.37484, 0.60233))
loop_1 = loop_1.lineTo(0.37598, 0.76988)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.64)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_64_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_64_interval_0.stl')