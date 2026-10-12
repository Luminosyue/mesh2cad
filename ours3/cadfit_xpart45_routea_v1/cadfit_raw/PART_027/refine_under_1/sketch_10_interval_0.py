import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.26954, -0.30304, 0.17946), normal=(0.00089, 0.99999, 0.00391), xDir=(1.0, -0.00089, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14644, 0.08964)
loop_1 = loop_1.lineTo(0.13333, 0.08813)
loop_1 = loop_1.lineTo(0.11375, 0.08128)
loop_1 = loop_1.lineTo(0.10345, 0.07598)
loop_1 = loop_1.lineTo(0.08483, 0.05645)
loop_1 = loop_1.lineTo(0.08047, 0.04241)
loop_1 = loop_1.lineTo(0.08287, 0.02183)
loop_1 = loop_1.lineTo(0.09996, 0.0239)
loop_1 = loop_1.lineTo(0.11687, 0.02507)
loop_1 = loop_1.threePointArc((0.15376, 0.02509), (0.19127, 0.02499))
loop_1 = loop_1.threePointArc((0.20019, 0.02492), (0.20692, 0.0249))
loop_1 = loop_1.threePointArc((0.21798, 0.02697), (0.22141, 0.03692))
loop_1 = loop_1.lineTo(0.22085, 0.05645)
loop_1 = loop_1.lineTo(0.20987, 0.06943)
loop_1 = loop_1.lineTo(0.18556, 0.08344)
loop_1 = loop_1.lineTo(0.17239, 0.08913)
loop_1 = loop_1.lineTo(0.15473, 0.09094)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_10_interval_0.stl')