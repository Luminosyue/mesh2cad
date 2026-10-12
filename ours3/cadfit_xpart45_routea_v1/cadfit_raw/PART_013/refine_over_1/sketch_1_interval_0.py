import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00843, -0.34986, 0.2646), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.51375, -0.44739)
loop_1 = loop_1.lineTo(0.51375, -0.54888)
loop_1 = loop_1.lineTo(0.43293, -0.54888)
loop_1 = loop_1.lineTo(0.45314, -0.52242)
loop_1 = loop_1.lineTo(0.46453, -0.50895)
loop_1 = loop_1.lineTo(0.49393, -0.47275)
loop_1 = loop_1.lineTo(0.5074, -0.45588)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_1_interval_0.stl')