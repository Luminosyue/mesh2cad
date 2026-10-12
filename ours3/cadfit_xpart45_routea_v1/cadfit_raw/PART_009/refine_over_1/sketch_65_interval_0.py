import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.315, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.97309, -0.08716)
loop_1 = loop_1.lineTo(-0.99234, -0.10411)
loop_1 = loop_1.threePointArc((-0.99415, -0.11695), (-0.99489, -0.12751))
loop_1 = loop_1.lineTo(-0.99442, 0.12323)
loop_1 = loop_1.lineTo(-0.93939, 0.00599)
loop_1 = loop_1.lineTo(-0.93311, -0.05458)
loop_1 = loop_1.threePointArc((-0.95025, -0.067), (-0.96055, -0.07632))
loop_1 = loop_1.lineTo(-0.97295, -0.08704)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.61)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_65_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_65_interval_0.stl')