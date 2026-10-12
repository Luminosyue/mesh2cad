import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.53029), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.12197, -0.98942)
loop_1 = loop_1.threePointArc((-0.10822, -0.99086), (-0.09498, -0.99188))
loop_1 = loop_1.lineTo(-0.48, -0.9917)
loop_1 = loop_1.lineTo(-0.47941, -0.8817)
loop_1 = loop_1.lineTo(-0.12227, -0.98942)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_85_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_85_interval_0.stl')