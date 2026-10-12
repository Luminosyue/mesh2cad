import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.7913, 0.2691, 0.01767), normal=(0.91138, 0.41151, -0.00634), xDir=(0.41152, -0.9114, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.24447, 0.56509)
loop_1 = loop_1.lineTo(-0.26678, 0.53519)
loop_1 = loop_1.lineTo(-0.27922, 0.51716)
loop_1 = loop_1.threePointArc((-0.2816, 0.49782), (-0.2833, 0.48153))
loop_1 = loop_1.lineTo(-0.28486, 0.46736)
loop_1 = loop_1.lineTo(-0.28633, 0.43691)
loop_1 = loop_1.lineTo(-0.28892, 0.41756)
loop_1 = loop_1.threePointArc((-0.28887, 0.4053), (-0.28883, 0.39583))
loop_1 = loop_1.lineTo(-0.29108, 0.37001)
loop_1 = loop_1.lineTo(-0.28729, 0.57204)
loop_1 = loop_1.lineTo(-0.23726, 0.57204)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_37_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_37_interval_1.stl')