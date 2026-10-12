import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45208, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02015, 0.29563)
loop_1 = loop_1.lineTo(-0.11978, 0.29544)
loop_1 = loop_1.lineTo(-0.09321, 0.29119)
loop_1 = loop_1.lineTo(-0.08018, 0.28266)
loop_1 = loop_1.lineTo(-0.05758, 0.26466)
loop_1 = loop_1.lineTo(-0.03949, 0.24699)
loop_1 = loop_1.lineTo(-0.02216, 0.22873)
loop_1 = loop_1.lineTo(-0.02015, 0.29553)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_40_interval_0.stl')