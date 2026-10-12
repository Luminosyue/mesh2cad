import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.94555, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.48213, 0.08718)
loop_1 = loop_1.lineTo(-0.45113, 0.07584)
loop_1 = loop_1.threePointArc((-0.41159, 0.06143), (-0.37104, 0.04611))
loop_1 = loop_1.lineTo(-0.27501, 0.01279)
loop_1 = loop_1.lineTo(-0.2011, -0.01191)
loop_1 = loop_1.threePointArc((-0.13809, -0.03385), (-0.07749, -0.05313))
loop_1 = loop_1.threePointArc((-0.02073, -0.06617), (0.03351, -0.07765))
loop_1 = loop_1.threePointArc((0.05809, -0.08296), (0.08145, -0.08692))
loop_1 = loop_1.threePointArc((0.12245, -0.0918), (0.1614, -0.09598))
loop_1 = loop_1.lineTo(0.12423, -0.08569)
loop_1 = loop_1.lineTo(-0.49203, 0.09095)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_55_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_55_interval_0.stl')