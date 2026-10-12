import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.07654, 0.898, 0.06141), normal=(0.09126, 0.99583, 0.00031), xDir=(0.99583, -0.09126, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03375, -0.00209)
loop_1 = loop_1.threePointArc((-0.0615, -0.00487), (-0.08812, -0.00776))
loop_1 = loop_1.lineTo(-0.11993, -0.0117)
loop_1 = loop_1.lineTo(-0.13097, -0.01366)
loop_1 = loop_1.lineTo(-0.16745, -0.01875)
loop_1 = loop_1.lineTo(-0.18734, -0.02256)
loop_1 = loop_1.lineTo(-0.21234, -0.02579)
loop_1 = loop_1.lineTo(-0.22915, -0.03014)
loop_1 = loop_1.lineTo(-0.22759, 0.12334)
loop_1 = loop_1.lineTo(-0.21671, 0.11735)
loop_1 = loop_1.lineTo(-0.03322, -0.00021)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_37_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_37_interval_1.stl')