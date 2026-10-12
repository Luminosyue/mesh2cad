import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.76547, -0.40851, -0.01757), normal=(0.92918, -0.36963, 0.00122), xDir=(-0.36963, -0.92918, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.22782, 0.12705)
loop_1 = loop_1.lineTo(-0.28745, 0.12705)
loop_1 = loop_1.lineTo(-0.2879, -0.02786)
loop_1 = loop_1.threePointArc((-0.28721, -0.00219), (-0.28719, 0.01326))
loop_1 = loop_1.lineTo(-0.28703, 0.042)
loop_1 = loop_1.lineTo(-0.28628, 0.07254)
loop_1 = loop_1.lineTo(-0.28676, 0.08674)
loop_1 = loop_1.lineTo(-0.27102, 0.09904)
loop_1 = loop_1.lineTo(-0.22955, 0.12593)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_6_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_6_interval_1.stl')