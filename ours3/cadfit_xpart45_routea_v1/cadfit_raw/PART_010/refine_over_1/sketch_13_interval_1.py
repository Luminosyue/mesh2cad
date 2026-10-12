import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.54398, -0.23239, -0.66889), normal=(-0.5224, -0.00284, -0.8527), xDir=(-0.00543, 0.99999, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12214, -0.17607)
loop_1 = loop_1.lineTo(0.35714, -0.17455)
loop_1 = loop_1.lineTo(0.32565, -0.13364)
loop_1 = loop_1.lineTo(0.2867, -0.08565)
loop_1 = loop_1.lineTo(0.26611, -0.05766)
loop_1 = loop_1.lineTo(0.24777, -0.03116)
loop_1 = loop_1.lineTo(0.22872, -0.00207)
loop_1 = loop_1.lineTo(0.19044, 0.02535)
loop_1 = loop_1.lineTo(0.14314, 0.03145)
loop_1 = loop_1.lineTo(0.12128, 0.03209)
loop_1 = loop_1.lineTo(0.12213, -0.17223)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_13_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_13_interval_1.stl')