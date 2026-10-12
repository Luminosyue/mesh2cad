import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.53664), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26715, 0.94854)
loop_1 = loop_1.lineTo(-0.24205, 0.95464)
loop_1 = loop_1.threePointArc((-0.27902, 0.94525), (-0.31996, 0.93442))
loop_1 = loop_1.threePointArc((-0.34911, 0.92484), (-0.37682, 0.91547))
loop_1 = loop_1.threePointArc((-0.40426, 0.90495), (-0.43034, 0.89472))
loop_1 = loop_1.threePointArc((-0.4546, 0.88359), (-0.47981, 0.87238))
loop_1 = loop_1.lineTo(-0.47959, 0.97601)
loop_1 = loop_1.lineTo(-0.26735, 0.94856)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_89_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_89_interval_0.stl')