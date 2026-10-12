import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21347), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.6137, -0.5173)
loop_1 = loop_1.threePointArc((0.61807, -0.51139), (0.62218, -0.50564))
loop_1 = loop_1.lineTo(0.63173, -0.49266)
loop_1 = loop_1.lineTo(0.63152, -0.55731)
loop_1 = loop_1.lineTo(0.58426, -0.55715)
loop_1 = loop_1.lineTo(0.6134, -0.51775)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_67_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_67_interval_0.stl')