import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.78191), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.38785, 0.00483)
loop_1 = loop_1.lineTo(-0.09617, -0.57133)
loop_1 = loop_1.lineTo(-0.1241, -0.55433)
loop_1 = loop_1.threePointArc((-0.13698, -0.54753), (-0.14876, -0.53877))
loop_1 = loop_1.lineTo(-0.17024, -0.52242)
loop_1 = loop_1.threePointArc((-0.17981, -0.51303), (-0.18863, -0.50282))
loop_1 = loop_1.lineTo(-0.21798, -0.4695)
loop_1 = loop_1.threePointArc((-0.23174, -0.45115), (-0.24514, -0.43197))
loop_1 = loop_1.threePointArc((-0.25721, -0.41219), (-0.26933, -0.39409))
loop_1 = loop_1.threePointArc((-0.28948, -0.36147), (-0.30928, -0.33099))
loop_1 = loop_1.threePointArc((-0.31701, -0.31468), (-0.32412, -0.29783))
loop_1 = loop_1.threePointArc((-0.32996, -0.28634), (-0.33445, -0.27423))
loop_1 = loop_1.threePointArc((-0.33744, -0.26677), (-0.34008, -0.26001))
loop_1 = loop_1.lineTo(-0.38785, -0.25954)
loop_1 = loop_1.lineTo(-0.38785, 0.00437)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.61)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_88_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_88_interval_0.stl')