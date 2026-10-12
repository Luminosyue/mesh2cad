import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.20298, 0.88874, -0.01508), normal=(0.22865, 0.97351, -0.00085), xDir=(0.97351, -0.22865, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.27172, 0.50513)
loop_1 = loop_1.lineTo(-0.30366, 0.50513)
loop_1 = loop_1.lineTo(-0.30346, 0.4146)
loop_1 = loop_1.lineTo(-0.29721, 0.45041)
loop_1 = loop_1.lineTo(-0.27891, 0.49413)
loop_1 = loop_1.lineTo(-0.27172, 0.50513)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_33_interval_0.stl')