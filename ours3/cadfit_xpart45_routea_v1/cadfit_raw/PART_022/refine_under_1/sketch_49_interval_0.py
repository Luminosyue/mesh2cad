import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.84835, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00466, 0.25189)
loop_1 = loop_1.threePointArc((0.05607, 0.25045), (0.11439, 0.25065))
loop_1 = loop_1.threePointArc((0.2826, 0.24797), (0.45711, 0.24368))
loop_1 = loop_1.lineTo(-0.43863, 0.24348)
loop_1 = loop_1.threePointArc((-0.37646, 0.24509), (-0.31743, 0.24779))
loop_1 = loop_1.threePointArc((-0.24073, 0.24978), (-0.16149, 0.25048))
loop_1 = loop_1.lineTo(-0.08019, 0.25063)
loop_1 = loop_1.threePointArc((-0.04319, 0.25129), (-0.00531, 0.25167))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.67)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_49_interval_0.stl')