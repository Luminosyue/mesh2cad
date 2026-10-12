import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.75659, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.65121, -0.56319)
loop_1 = loop_1.lineTo(0.63221, -0.56978)
loop_1 = loop_1.threePointArc((0.6039, -0.57323), (0.57474, -0.57581))
loop_1 = loop_1.threePointArc((0.54817, -0.57658), (0.52092, -0.57676))
loop_1 = loop_1.lineTo(0.10538, -0.53234)
loop_1 = loop_1.lineTo(0.10578, -0.61268)
loop_1 = loop_1.lineTo(0.40226, -0.61293)
loop_1 = loop_1.threePointArc((0.46224, -0.61367), (0.52426, -0.61524))
loop_1 = loop_1.lineTo(0.55455, -0.61293)
loop_1 = loop_1.lineTo(0.58872, -0.60585)
loop_1 = loop_1.lineTo(0.62717, -0.5903)
loop_1 = loop_1.lineTo(0.64788, -0.58043)
loop_1 = loop_1.lineTo(0.66724, -0.55763)
loop_1 = loop_1.threePointArc((0.65497, -0.56185), (0.65158, -0.5631))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_34_interval_0.stl')