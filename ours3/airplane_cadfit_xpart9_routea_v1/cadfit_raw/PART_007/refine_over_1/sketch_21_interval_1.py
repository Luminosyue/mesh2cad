import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.66715, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17799, -0.05755)
loop_1 = loop_1.lineTo(0.15698, -0.07151)
loop_1 = loop_1.threePointArc((0.1412, -0.07984), (0.13356, -0.08345))
loop_1 = loop_1.lineTo(0.11494, -0.0909)
loop_1 = loop_1.lineTo(0.0944, -0.09493)
loop_1 = loop_1.threePointArc((0.07992, -0.09469), (0.07115, -0.09414))
loop_1 = loop_1.lineTo(0.05548, -0.09234)
loop_1 = loop_1.lineTo(0.11345, -0.13028)
loop_1 = loop_1.threePointArc((0.14197, -0.09826), (0.1692, -0.06753))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_21_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_21_interval_1.stl')