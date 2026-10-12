import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.16229, 0.064)
loop_1 = loop_1.lineTo(0.1341, 0.14455)
loop_1 = loop_1.threePointArc((0.12682, 0.14208), (0.12076, 0.14012))
loop_1 = loop_1.threePointArc((0.12745, 0.14237), (0.13626, 0.14531))
loop_1 = loop_1.threePointArc((0.14543, 0.14644), (0.1529, 0.14738))
loop_1 = loop_1.lineTo(0.17125, 0.14521)
loop_1 = loop_1.threePointArc((0.17875, 0.14167), (0.18651, 0.13787))
loop_1 = loop_1.lineTo(0.19766, 0.12178)
loop_1 = loop_1.lineTo(0.16229, 0.064)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_35_interval_0.stl')