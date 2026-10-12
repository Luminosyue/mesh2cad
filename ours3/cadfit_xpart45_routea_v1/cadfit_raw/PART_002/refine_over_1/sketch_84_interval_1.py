import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.19373, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39225, 0.77)
loop_1 = loop_1.lineTo(-0.3921, 0.72323)
loop_1 = loop_1.lineTo(-0.37779, 0.73313)
loop_1 = loop_1.threePointArc((-0.36845, 0.74032), (-0.35866, 0.74763))
loop_1 = loop_1.threePointArc((-0.34976, 0.75439), (-0.34132, 0.76091))
loop_1 = loop_1.lineTo(-0.39219, 0.77)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_84_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_84_interval_1.stl')