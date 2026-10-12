import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0075, 0.07, 0.07756), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.88912, 0.59708)
loop_1 = loop_1.lineTo(-0.86544, 0.63928)
loop_1 = loop_1.lineTo(-0.81542, 0.66631)
loop_1 = loop_1.lineTo(-0.76359, 0.66827)
loop_1 = loop_1.lineTo(-0.6274, 0.66758)
loop_1 = loop_1.lineTo(-0.4719, 0.66664)
loop_1 = loop_1.lineTo(-0.45564, 0.66632)
loop_1 = loop_1.threePointArc((-0.34463, 0.66682), (-0.229, 0.66583))
loop_1 = loop_1.lineTo(-0.21274, 0.66642)
loop_1 = loop_1.lineTo(0.13384, 0.66579)
loop_1 = loop_1.lineTo(0.18567, 0.66616)
loop_1 = loop_1.lineTo(0.39301, 0.66577)
loop_1 = loop_1.lineTo(0.78836, 0.66505)
loop_1 = loop_1.lineTo(0.8402, 0.64695)
loop_1 = loop_1.lineTo(0.82886, 0.64048)
loop_1 = loop_1.lineTo(-0.87159, 0.59752)
loop_1 = loop_1.lineTo(-0.88912, 0.59708)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.55)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_6_interval_0.stl')