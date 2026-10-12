import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.1365), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08119, 0.927)
loop_1 = loop_1.threePointArc((-0.08822, 0.92662), (-0.09488, 0.92542))
loop_1 = loop_1.lineTo(-0.14439, 0.91748)
loop_1 = loop_1.threePointArc((-0.16985, 0.91217), (-0.19389, 0.90684))
loop_1 = loop_1.lineTo(-0.24635, 0.89233)
loop_1 = loop_1.lineTo(-0.30203, 0.87531)
loop_1 = loop_1.threePointArc((-0.32616, 0.86875), (-0.34888, 0.8621))
loop_1 = loop_1.lineTo(-0.40134, 0.84528)
loop_1 = loop_1.threePointArc((-0.4177, 0.8379), (-0.4327, 0.83016))
loop_1 = loop_1.lineTo(-0.45288, 0.81983)
loop_1 = loop_1.lineTo(-0.48, 0.8033)
loop_1 = loop_1.lineTo(-0.47928, 0.92765)
loop_1 = loop_1.lineTo(-0.07585, 0.92715)
loop_1 = loop_1.lineTo(-0.03084, 0.92873)
loop_1 = loop_1.lineTo(-0.08141, 0.92698)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_84_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_84_interval_1.stl')