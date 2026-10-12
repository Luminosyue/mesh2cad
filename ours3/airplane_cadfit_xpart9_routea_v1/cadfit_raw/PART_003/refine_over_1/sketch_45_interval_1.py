import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.13084, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.77849, -0.01933)
loop_1 = loop_1.lineTo(-0.20887, -0.0204)
loop_1 = loop_1.threePointArc((-0.25143, -0.03351), (-0.2913, -0.04761))
loop_1 = loop_1.threePointArc((-0.34777, -0.06496), (-0.40126, -0.08241))
loop_1 = loop_1.threePointArc((-0.41624, -0.08642), (-0.42999, -0.09082))
loop_1 = loop_1.threePointArc((-0.48328, -0.11062), (-0.5337, -0.13031))
loop_1 = loop_1.threePointArc((-0.55496, -0.13474), (-0.57465, -0.13979))
loop_1 = loop_1.threePointArc((-0.60931, -0.15049), (-0.64189, -0.16146))
loop_1 = loop_1.threePointArc((-0.66571, -0.16872), (-0.68796, -0.17617))
loop_1 = loop_1.threePointArc((-0.7119, -0.18483), (-0.73699, -0.1918))
loop_1 = loop_1.threePointArc((-0.746, -0.19492), (-0.75401, -0.19831))
loop_1 = loop_1.lineTo(-0.77769, -0.20789)
loop_1 = loop_1.lineTo(-0.77849, -0.01979)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_45_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_45_interval_1.stl')