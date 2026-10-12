import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.1487, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.89423, 0.3863)
loop_1 = loop_1.lineTo(0.91526, 0.37321)
loop_1 = loop_1.lineTo(0.95281, 0.3344)
loop_1 = loop_1.threePointArc((0.96812, 0.30571), (0.98372, 0.27582))
loop_1 = loop_1.lineTo(0.86266, 0.2471)
loop_1 = loop_1.lineTo(0.87646, 0.25495)
loop_1 = loop_1.threePointArc((0.89309, 0.26974), (0.90873, 0.2841))
loop_1 = loop_1.threePointArc((0.91737, 0.30072), (0.92295, 0.31361))
loop_1 = loop_1.lineTo(0.92274, 0.35011)
loop_1 = loop_1.threePointArc((0.91635, 0.36209), (0.91105, 0.36982))
loop_1 = loop_1.lineTo(0.89433, 0.3862)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_50_interval_0.stl')