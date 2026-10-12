import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.82681, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11377, 0.24759)
loop_1 = loop_1.lineTo(0.00512, 0.24723)
loop_1 = loop_1.lineTo(0.14726, 0.24719)
loop_1 = loop_1.threePointArc((0.20998, 0.24719), (0.27464, 0.24623))
loop_1 = loop_1.lineTo(0.45568, 0.24681)
loop_1 = loop_1.lineTo(0.525, 0.24518)
loop_1 = loop_1.threePointArc((0.62288, 0.24312), (0.72407, 0.23828))
loop_1 = loop_1.threePointArc((0.65057, 0.24063), (0.57477, 0.24299))
loop_1 = loop_1.lineTo(0.42016, 0.24529)
loop_1 = loop_1.threePointArc((0.25139, 0.24471), (0.09001, 0.24306))
loop_1 = loop_1.threePointArc((-0.05092, 0.24463), (-0.19703, 0.2465))
loop_1 = loop_1.threePointArc((-0.15457, 0.24699), (-0.11443, 0.24768))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.61)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_45_interval_0.stl')