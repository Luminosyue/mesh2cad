import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.17218, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.35634, -0.34131)
loop_1 = loop_1.lineTo(0.37529, -0.34598)
loop_1 = loop_1.lineTo(0.38812, -0.35531)
loop_1 = loop_1.lineTo(0.37462, -0.36735)
loop_1 = loop_1.lineTo(0.32786, -0.36898)
loop_1 = loop_1.lineTo(0.32167, -0.35402)
loop_1 = loop_1.lineTo(0.33507, -0.34839)
loop_1 = loop_1.lineTo(0.34632, -0.34251)
loop_1 = loop_1.lineTo(0.35634, -0.34131)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_44_interval_0.stl')