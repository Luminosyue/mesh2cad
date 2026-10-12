import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.52664), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0541, 0.97606)
loop_1 = loop_1.lineTo(0.42, 0.97511)
loop_1 = loop_1.lineTo(0.41944, 0.87621)
loop_1 = loop_1.lineTo(0.39948, 0.88652)
loop_1 = loop_1.threePointArc((0.37142, 0.8988), (0.34448, 0.90983))
loop_1 = loop_1.lineTo(0.29476, 0.92744)
loop_1 = loop_1.lineTo(0.25262, 0.93892)
loop_1 = loop_1.lineTo(0.09451, 0.96899)
loop_1 = loop_1.threePointArc((0.06799, 0.97221), (0.04278, 0.97488))
loop_1 = loop_1.lineTo(0.00609, 0.97593)
loop_1 = loop_1.lineTo(0.05378, 0.97606)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_88_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_88_interval_0.stl')