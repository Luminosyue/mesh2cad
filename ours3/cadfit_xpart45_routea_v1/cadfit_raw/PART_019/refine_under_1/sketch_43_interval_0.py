import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.62489, -0.11543, 0.72252), normal=(-0.56463, 0.00224, -0.82534), xDir=(0.00397, 0.99999, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.61365, -0.42187)
loop_1 = loop_1.lineTo(0.83636, -0.42294)
loop_1 = loop_1.lineTo(0.83842, 0.20689)
loop_1 = loop_1.lineTo(-0.61157, 0.21433)
loop_1 = loop_1.lineTo(-0.61364, -0.41792)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_43_interval_0.stl')