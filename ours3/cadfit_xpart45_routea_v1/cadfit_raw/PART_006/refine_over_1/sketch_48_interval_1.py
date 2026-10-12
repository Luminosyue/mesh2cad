import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.92717, -0.1142, -0.48273), normal=(0.98532, 0.0, -0.17071), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.22697, -0.23589)
loop_1 = loop_1.lineTo(-0.10794, 0.09882)
loop_1 = loop_1.lineTo(-0.5042, 0.09882)
loop_1 = loop_1.lineTo(-0.5042, -0.3443)
loop_1 = loop_1.lineTo(-0.11987, -0.3443)
loop_1 = loop_1.lineTo(-0.16245, -0.31975)
loop_1 = loop_1.lineTo(-0.18383, -0.29787)
loop_1 = loop_1.lineTo(-0.20535, -0.26889)
loop_1 = loop_1.lineTo(-0.2228, -0.24228)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_48_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_48_interval_1.stl')