import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.01, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.22065, 0.03059)
loop_1 = loop_1.lineTo(-0.26633, 0.02898)
loop_1 = loop_1.lineTo(-0.26528, 0.01291)
loop_1 = loop_1.lineTo(-0.26435, -0.01)
loop_1 = loop_1.lineTo(-0.15838, -0.00975)
loop_1 = loop_1.lineTo(-0.1673, 0.01356)
loop_1 = loop_1.lineTo(-0.18205, 0.01737)
loop_1 = loop_1.lineTo(-0.19536, 0.01157)
loop_1 = loop_1.lineTo(-0.217, 0.02415)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_57_interval_0.stl')