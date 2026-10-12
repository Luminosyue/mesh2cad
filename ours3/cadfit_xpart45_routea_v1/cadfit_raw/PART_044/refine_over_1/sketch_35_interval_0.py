import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.10001, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06051, 0.60343)
loop_1 = loop_1.lineTo(0.066, 0.58846)
loop_1 = loop_1.lineTo(0.06747, 0.57818)
loop_1 = loop_1.lineTo(0.06614, 0.54697)
loop_1 = loop_1.threePointArc((0.06493, 0.53615), (0.06412, 0.5259))
loop_1 = loop_1.threePointArc((0.06381, 0.5172), (0.06313, 0.50834))
loop_1 = loop_1.threePointArc((0.06483, 0.48563), (0.06704, 0.46407))
loop_1 = loop_1.lineTo(0.07083, 0.44682)
loop_1 = loop_1.threePointArc((0.07213, 0.43729), (0.07323, 0.42733))
loop_1 = loop_1.lineTo(0.07139, 0.41263)
loop_1 = loop_1.lineTo(0.06619, 0.39677)
loop_1 = loop_1.threePointArc((0.06415, 0.3909), (0.06242, 0.38537))
loop_1 = loop_1.lineTo(0.06416, 0.36617)
loop_1 = loop_1.lineTo(0.06051, 0.34024)
loop_1 = loop_1.lineTo(0.06051, 0.60325)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_35_interval_0.stl')