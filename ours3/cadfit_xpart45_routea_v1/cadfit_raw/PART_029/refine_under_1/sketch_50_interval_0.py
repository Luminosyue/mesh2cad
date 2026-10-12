import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.01, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.88704, 0.1744)
loop_1 = loop_1.lineTo(-0.90275, 0.16991)
loop_1 = loop_1.lineTo(-0.91729, 0.16468)
loop_1 = loop_1.lineTo(-0.9315, 0.15653)
loop_1 = loop_1.lineTo(-0.94505, 0.14624)
loop_1 = loop_1.lineTo(-0.95865, 0.13092)
loop_1 = loop_1.lineTo(-0.79324, 0.13127)
loop_1 = loop_1.threePointArc((-0.80878, 0.1427), (-0.81627, 0.14757))
loop_1 = loop_1.lineTo(-0.83218, 0.15657)
loop_1 = loop_1.lineTo(-0.84469, 0.16335)
loop_1 = loop_1.threePointArc((-0.85177, 0.1663), (-0.85893, 0.16954))
loop_1 = loop_1.lineTo(-0.8729, 0.17386)
loop_1 = loop_1.lineTo(-0.88475, 0.17421)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_50_interval_0.stl')