import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.91714, 0.08452, 0.00943), normal=(0.9762, 0.21686, 0.00033), xDir=(0.21686, -0.9762, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.33133, 0.52964)
loop_1 = loop_1.lineTo(-0.37753, 0.52964)
loop_1 = loop_1.lineTo(-0.37761, 0.46853)
loop_1 = loop_1.lineTo(-0.36782, 0.48678)
loop_1 = loop_1.lineTo(-0.33636, 0.52692)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_26_interval_0.stl')