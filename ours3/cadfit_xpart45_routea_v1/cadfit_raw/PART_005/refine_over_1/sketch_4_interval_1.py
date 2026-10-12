import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.55834, 0.62541, -0.07693), normal=(-0.66585, 0.74608, -0.00024), xDir=(0.74608, 0.66585, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39799, 0.50344)
loop_1 = loop_1.threePointArc((-0.42011, 0.49133), (-0.44002, 0.47755))
loop_1 = loop_1.lineTo(-0.46803, 0.44865)
loop_1 = loop_1.lineTo(-0.48309, 0.40088)
loop_1 = loop_1.lineTo(-0.48722, 0.27805)
loop_1 = loop_1.threePointArc((-0.48939, 0.17325), (-0.49019, 0.07851))
loop_1 = loop_1.lineTo(-0.47637, 0.02829)
loop_1 = loop_1.lineTo(-0.47103, 0.01821)
loop_1 = loop_1.lineTo(-0.46412, 0.00674)
loop_1 = loop_1.lineTo(-0.44953, -0.01385)
loop_1 = loop_1.lineTo(-0.39815, -0.068)
loop_1 = loop_1.lineTo(-0.398, 0.50235)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_4_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_4_interval_1.stl')