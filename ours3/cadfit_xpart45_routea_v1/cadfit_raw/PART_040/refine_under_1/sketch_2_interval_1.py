import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.78835, 0.1851, -0.02292), normal=(-0.67466, 0.73812, 0.0012), xDir=(0.73812, 0.67466, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11129, -0.19701)
loop_1 = loop_1.lineTo(-0.11081, 0.15299)
loop_1 = loop_1.threePointArc((-0.12415, 0.15299), (-0.13352, 0.15299))
loop_1 = loop_1.lineTo(-0.134, -0.19701)
loop_1 = loop_1.lineTo(-0.11145, -0.19701)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_2_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_2_interval_1.stl')