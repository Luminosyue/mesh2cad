import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.4, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0518, 0.99949)
loop_1 = loop_1.threePointArc((0.06003, 0.99768), (0.06713, 0.99253))
loop_1 = loop_1.lineTo(0.0696, -0.01479)
loop_1 = loop_1.threePointArc((0.07126, -0.48939), (0.06854, -0.98225))
loop_1 = loop_1.threePointArc((0.0626, -0.9894), (0.0555, -0.99117))
loop_1 = loop_1.threePointArc((0.00599, -0.99268), (-0.04416, -0.99156))
loop_1 = loop_1.threePointArc((-0.05095, -0.98912), (-0.05591, -0.98546))
loop_1 = loop_1.threePointArc((-0.06032, -0.49172), (-0.06719, -0.0253))
loop_1 = loop_1.threePointArc((-0.06504, 0.18459), (-0.05992, 0.40133))
loop_1 = loop_1.threePointArc((-0.05902, 0.70169), (-0.06093, 0.98867))
loop_1 = loop_1.lineTo(-0.04489, 0.99946)
loop_1 = loop_1.threePointArc((0.00365, 0.99942), (0.05025, 0.99973))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.8)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/speaker_big_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw/PART_002/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/speaker_big_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw/PART_002/sketch_5_interval_0.stl')