import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.66826, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08078, -0.12413)
loop_1 = loop_1.lineTo(0.08045, -0.26486)
loop_1 = loop_1.threePointArc((0.08026, -0.33254), (0.08076, -0.3971))
loop_1 = loop_1.threePointArc((0.08049, -0.45767), (0.07979, -0.5203))
loop_1 = loop_1.lineTo(0.07909, -0.55423)
loop_1 = loop_1.threePointArc((0.07752, -0.61364), (0.07479, -0.67503))
loop_1 = loop_1.threePointArc((0.07504, -0.70075), (0.07456, -0.72707))
loop_1 = loop_1.threePointArc((0.07313, -0.74832), (0.07148, -0.77))
loop_1 = loop_1.lineTo(0.08078, -0.1245)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_27_interval_0.stl')