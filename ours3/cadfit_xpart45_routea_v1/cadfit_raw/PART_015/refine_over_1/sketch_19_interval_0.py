import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03469, -0.15005, -0.28887), normal=(-0.00152, -0.05475, 0.9985), xDir=(-0.0, 0.9985, 0.05475))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.90446, -0.57749)
loop_1 = loop_1.lineTo(0.95763, -0.57749)
loop_1 = loop_1.lineTo(0.95768, -0.49728)
loop_1 = loop_1.lineTo(0.9519, -0.50832)
loop_1 = loop_1.lineTo(0.94307, -0.52456)
loop_1 = loop_1.lineTo(0.9198, -0.55736)
loop_1 = loop_1.lineTo(0.90731, -0.57387)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.48)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_19_interval_0.stl')