import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.26953, -0.29304, 0.1795), normal=(0.00089, 0.99999, 0.00391), xDir=(1.0, -0.00089, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.24345, -0.02745)
loop_1 = loop_1.threePointArc((-0.25271, -0.0319), (-0.26156, -0.03628))
loop_1 = loop_1.lineTo(-0.28776, -0.06213)
loop_1 = loop_1.lineTo(-0.28992, -0.07599)
loop_1 = loop_1.lineTo(-0.29049, -0.08761)
loop_1 = loop_1.lineTo(-0.28851, -0.0998)
loop_1 = loop_1.lineTo(-0.27683, -0.11793)
loop_1 = loop_1.lineTo(-0.26135, -0.12838)
loop_1 = loop_1.lineTo(-0.24178, -0.13346)
loop_1 = loop_1.lineTo(-0.24239, -0.11489)
loop_1 = loop_1.lineTo(-0.2427, -0.05397)
loop_1 = loop_1.lineTo(-0.24157, -0.02771)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_11_interval_0.stl')