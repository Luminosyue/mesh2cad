import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07489, 0.069, 0.55018), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.549, 0.801)
loop_1 = loop_1.lineTo(0.549, 0.8973)
loop_1 = loop_1.lineTo(0.12761, 0.8975)
loop_1 = loop_1.lineTo(0.08835, 0.89778)
loop_1 = loop_1.lineTo(0.54268, 0.79741)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_36_interval_0.stl')