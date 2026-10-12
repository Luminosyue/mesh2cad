import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.69634, 0.50672, 0.49536), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03962, 0.11466)
loop_1 = loop_1.lineTo(-0.01931, 0.09873)
loop_1 = loop_1.lineTo(-0.00663, 0.0866)
loop_1 = loop_1.lineTo(-0.01213, 0.06955)
loop_1 = loop_1.lineTo(-0.01767, 0.05017)
loop_1 = loop_1.lineTo(-0.03033, 0.04023)
loop_1 = loop_1.lineTo(-0.04254, 0.03604)
loop_1 = loop_1.lineTo(-0.07621, 0.04365)
loop_1 = loop_1.lineTo(-0.07478, 0.05898)
loop_1 = loop_1.lineTo(-0.05836, 0.0866)
loop_1 = loop_1.lineTo(-0.04058, 0.11301)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_18_interval_0.stl')