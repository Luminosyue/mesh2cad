import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.8403, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.05301, 0.01809)
loop_1 = loop_1.lineTo(0.10962, 0.07172)
loop_1 = loop_1.lineTo(0.00073, 0.07143)
loop_1 = loop_1.lineTo(0.0155, 0.05363)
loop_1 = loop_1.lineTo(0.03004, 0.03545)
loop_1 = loop_1.lineTo(0.04575, 0.0145)
loop_1 = loop_1.lineTo(0.0574, 0.01485)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.78)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_35_interval_0.stl')