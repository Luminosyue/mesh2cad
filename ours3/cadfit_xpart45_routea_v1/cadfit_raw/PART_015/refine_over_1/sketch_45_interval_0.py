import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21825), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.78103, -0.54208)
loop_1 = loop_1.lineTo(0.8297, -0.54193)
loop_1 = loop_1.lineTo(0.82953, -0.46321)
loop_1 = loop_1.lineTo(0.82327, -0.47442)
loop_1 = loop_1.threePointArc((0.81932, -0.48108), (0.81511, -0.48787))
loop_1 = loop_1.lineTo(0.79339, -0.52314)
loop_1 = loop_1.threePointArc((0.78708, -0.5328), (0.78107, -0.54202))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_45_interval_0.stl')