import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01944, 0.25619, 0.655), normal=(-0.0, 0.23236, 0.97263), xDir=(0.0, 0.97263, -0.23236))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.4081, 0.34944)
loop_1 = loop_1.lineTo(-0.48112, 0.34931)
loop_1 = loop_1.lineTo(-0.4733, 0.30989)
loop_1 = loop_1.threePointArc((-0.46791, 0.28921), (-0.46348, 0.27125))
loop_1 = loop_1.lineTo(-0.4438, 0.20038)
loop_1 = loop_1.lineTo(-0.44023, 0.18973)
loop_1 = loop_1.lineTo(-0.4365, 0.17189)
loop_1 = loop_1.lineTo(-0.43127, 0.15526)
loop_1 = loop_1.lineTo(-0.42883, 0.13521)
loop_1 = loop_1.lineTo(-0.42445, 0.1167)
loop_1 = loop_1.lineTo(-0.42163, 0.09738)
loop_1 = loop_1.threePointArc((-0.41622, 0.07266), (-0.41201, 0.05087))
loop_1 = loop_1.threePointArc((-0.40961, 0.03312), (-0.40809, 0.01984))
loop_1 = loop_1.lineTo(-0.4081, 0.34577)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_26_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_26_interval_1.stl')