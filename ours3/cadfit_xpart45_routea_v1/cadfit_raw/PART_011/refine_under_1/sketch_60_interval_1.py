import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.19, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.77498, 0.20465)
loop_1 = loop_1.lineTo(-0.78011, 0.19072)
loop_1 = loop_1.threePointArc((-0.78056, 0.13794), (-0.78051, 0.08751))
loop_1 = loop_1.threePointArc((-0.78154, 0.01515), (-0.78122, -0.05409))
loop_1 = loop_1.lineTo(-0.78285, -0.09972)
loop_1 = loop_1.lineTo(-0.7786, -0.1462)
loop_1 = loop_1.lineTo(-0.77498, 0.20441)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_60_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_60_interval_1.stl')