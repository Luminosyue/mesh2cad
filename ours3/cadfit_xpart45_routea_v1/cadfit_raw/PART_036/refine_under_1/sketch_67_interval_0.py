import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.17741), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17217, 0.28329)
loop_1 = loop_1.lineTo(-0.15222, 0.27894)
loop_1 = loop_1.threePointArc((-0.1435, 0.27658), (-0.13678, 0.27469))
loop_1 = loop_1.lineTo(-0.11765, 0.27266)
loop_1 = loop_1.lineTo(-0.11356, 0.25768)
loop_1 = loop_1.lineTo(-0.11273, 0.2305)
loop_1 = loop_1.lineTo(-0.15657, 0.22851)
loop_1 = loop_1.lineTo(-0.16939, 0.22912)
loop_1 = loop_1.threePointArc((-0.17083, 0.23641), (-0.17232, 0.24338))
loop_1 = loop_1.lineTo(-0.17469, 0.2544)
loop_1 = loop_1.lineTo(-0.17573, 0.28318)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_67_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_67_interval_0.stl')