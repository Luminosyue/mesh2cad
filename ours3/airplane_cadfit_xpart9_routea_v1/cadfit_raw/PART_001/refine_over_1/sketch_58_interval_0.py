import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.92155, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.58873, 0.09621)
loop_1 = loop_1.lineTo(-0.57956, 0.08136)
loop_1 = loop_1.threePointArc((-0.56007, 0.06867), (-0.54926, 0.06322))
loop_1 = loop_1.lineTo(-0.5351, 0.05576)
loop_1 = loop_1.threePointArc((-0.5205, 0.04784), (-0.5055, 0.03954))
loop_1 = loop_1.threePointArc((-0.48366, 0.02762), (-0.46243, 0.017))
loop_1 = loop_1.threePointArc((-0.45264, 0.01238), (-0.44331, 0.00815))
loop_1 = loop_1.threePointArc((-0.42988, 0.00188), (-0.41701, -0.00382))
loop_1 = loop_1.lineTo(-0.58873, -0.00345)
loop_1 = loop_1.lineTo(-0.58873, 0.09605)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.9)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_58_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_58_interval_0.stl')