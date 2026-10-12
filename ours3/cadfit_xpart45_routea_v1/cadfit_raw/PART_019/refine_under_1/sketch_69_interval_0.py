import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.51), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.66307, -0.9095)
loop_1 = loop_1.threePointArc((-0.64853, -0.91047), (-0.63454, -0.91011))
loop_1 = loop_1.threePointArc((-0.54458, -0.91062), (-0.45166, -0.91231))
loop_1 = loop_1.lineTo(-0.33336, -0.91174)
loop_1 = loop_1.threePointArc((-0.22896, -0.91476), (-0.12939, -0.91393))
loop_1 = loop_1.threePointArc((-0.08921, -0.91279), (-0.0481, -0.91359))
loop_1 = loop_1.threePointArc((0.02227, -0.91353), (0.0948, -0.91468))
loop_1 = loop_1.lineTo(0.22327, -0.91227)
loop_1 = loop_1.threePointArc((0.25473, -0.9131), (0.28423, -0.91275))
loop_1 = loop_1.threePointArc((0.33722, -0.91118), (0.39167, -0.9119))
loop_1 = loop_1.lineTo(0.42186, -0.90946)
loop_1 = loop_1.lineTo(-0.66233, -0.90946)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.96)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_69_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_69_interval_0.stl')