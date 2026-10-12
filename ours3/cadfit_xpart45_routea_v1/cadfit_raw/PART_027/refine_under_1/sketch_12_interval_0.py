import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.57206, -0.29011, 0.24464), normal=(0.99995, 0.00076, 0.01012), xDir=(0.00076, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05839, 0.02421)
loop_1 = loop_1.threePointArc((-0.05769, 0.01668), (-0.05692, 0.00946))
loop_1 = loop_1.lineTo(-0.05694, -0.0602)
loop_1 = loop_1.threePointArc((-0.05755, -0.06935), (-0.05796, -0.07679))
loop_1 = loop_1.lineTo(-0.04094, -0.06572)
loop_1 = loop_1.lineTo(-0.03049, -0.05734)
loop_1 = loop_1.threePointArc((-0.02261, -0.04947), (-0.01985, -0.04573))
loop_1 = loop_1.lineTo(-0.00949, -0.01396)
loop_1 = loop_1.lineTo(-0.02932, 0.01103)
loop_1 = loop_1.lineTo(-0.0418, 0.01814)
loop_1 = loop_1.lineTo(-0.05765, 0.024)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_12_interval_0.stl')