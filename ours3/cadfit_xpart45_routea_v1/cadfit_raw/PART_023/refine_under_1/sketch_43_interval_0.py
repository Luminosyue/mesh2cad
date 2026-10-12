import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.22573, -0.06266, 0.01644), normal=(0.86268, -0.50576, -0.00026), xDir=(-0.50576, -0.86268, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.57698, 0.74062)
loop_1 = loop_1.threePointArc((0.57912, 0.73146), (0.58128, 0.7219))
loop_1 = loop_1.lineTo(0.59528, 0.70467)
loop_1 = loop_1.lineTo(0.60047, 0.69362)
loop_1 = loop_1.lineTo(0.59857, 0.67688)
loop_1 = loop_1.threePointArc((0.59145, 0.65845), (0.58697, 0.64807))
loop_1 = loop_1.lineTo(0.58125, 0.62786)
loop_1 = loop_1.lineTo(0.5784, 0.6084)
loop_1 = loop_1.threePointArc((0.57788, 0.59788), (0.5771, 0.58693))
loop_1 = loop_1.lineTo(0.57723, 0.56535)
loop_1 = loop_1.threePointArc((0.57741, 0.54415), (0.57793, 0.52623))
loop_1 = loop_1.lineTo(0.57794, 0.51456)
loop_1 = loop_1.lineTo(0.57687, 0.492)
loop_1 = loop_1.lineTo(0.57698, 0.73795)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_43_interval_0.stl')