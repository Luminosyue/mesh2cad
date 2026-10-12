import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.64999, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.39444, 0.29103)
loop_1 = loop_1.threePointArc((0.41013, 0.29008), (0.42521, 0.2897))
loop_1 = loop_1.lineTo(0.39704, 0.29112)
loop_1 = loop_1.lineTo(0.69386, 0.31793)
loop_1 = loop_1.lineTo(0.21906, 0.29129)
loop_1 = loop_1.threePointArc((0.25163, 0.29133), (0.28255, 0.2919))
loop_1 = loop_1.lineTo(0.34028, 0.29084)
loop_1 = loop_1.threePointArc((0.36387, 0.29134), (0.38808, 0.29133))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_32_interval_0.stl')