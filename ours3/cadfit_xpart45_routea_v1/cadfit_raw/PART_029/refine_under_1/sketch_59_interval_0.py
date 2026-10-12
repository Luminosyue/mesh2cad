import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.12), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02477, 0.80795)
loop_1 = loop_1.lineTo(-0.00389, 0.78515)
loop_1 = loop_1.lineTo(0.00711, 0.77865)
loop_1 = loop_1.lineTo(0.03228, 0.76987)
loop_1 = loop_1.lineTo(0.0586, 0.7647)
loop_1 = loop_1.lineTo(0.03637, 0.74861)
loop_1 = loop_1.lineTo(0.02187, 0.74359)
loop_1 = loop_1.lineTo(0.00766, 0.74081)
loop_1 = loop_1.lineTo(-0.00783, 0.73828)
loop_1 = loop_1.lineTo(-0.02163, 0.73388)
loop_1 = loop_1.lineTo(-0.0281, 0.81223)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_59_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_59_interval_0.stl')