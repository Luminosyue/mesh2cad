import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.59362, 0.01506, 0.36259), normal=(0.82805, -0.00087, -0.56066), xDir=(-0.00105, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.52625, 0.11347)
loop_1 = loop_1.lineTo(0.83525, 0.11017)
loop_1 = loop_1.lineTo(0.94096, 0.11051)
loop_1 = loop_1.lineTo(0.98246, 0.06541)
loop_1 = loop_1.lineTo(0.98747, 0.0543)
loop_1 = loop_1.lineTo(0.97136, 0.04466)
loop_1 = loop_1.lineTo(-0.97819, 0.04466)
loop_1 = loop_1.threePointArc((-0.96185, 0.07782), (-0.94566, 0.10281))
loop_1 = loop_1.threePointArc((-0.88807, 0.10529), (-0.83048, 0.10291))
loop_1 = loop_1.threePointArc((-0.16562, 0.10975), (0.52418, 0.1133))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_35_interval_0.stl')