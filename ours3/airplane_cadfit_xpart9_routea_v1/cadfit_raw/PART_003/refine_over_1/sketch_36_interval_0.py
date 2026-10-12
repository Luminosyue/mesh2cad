import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.8403, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02015, -0.33571)
loop_1 = loop_1.lineTo(0.02798, -0.35007)
loop_1 = loop_1.lineTo(0.04561, -0.37156)
loop_1 = loop_1.lineTo(0.06359, -0.38517)
loop_1 = loop_1.lineTo(0.08262, -0.39526)
loop_1 = loop_1.lineTo(0.09422, -0.39736)
loop_1 = loop_1.lineTo(0.02015, -0.3972)
loop_1 = loop_1.lineTo(0.02015, -0.33579)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.84)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_36_interval_0.stl')