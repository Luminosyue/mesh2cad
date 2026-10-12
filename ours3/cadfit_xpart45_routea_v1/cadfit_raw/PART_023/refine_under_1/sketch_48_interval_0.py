import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.3547, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.5868, 0.97836)
loop_1 = loop_1.lineTo(0.61263, 0.97757)
loop_1 = loop_1.threePointArc((0.61896, 0.97601), (0.62539, 0.97427))
loop_1 = loop_1.lineTo(0.65079, 0.96636)
loop_1 = loop_1.lineTo(0.45984, 0.96054)
loop_1 = loop_1.lineTo(0.47647, 0.97032)
loop_1 = loop_1.lineTo(0.48753, 0.97137)
loop_1 = loop_1.lineTo(0.5034, 0.97771)
loop_1 = loop_1.threePointArc((0.51082, 0.97751), (0.5178, 0.97777))
loop_1 = loop_1.threePointArc((0.53513, 0.97815), (0.55304, 0.97817))
loop_1 = loop_1.threePointArc((0.57026, 0.97827), (0.58667, 0.97836))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.29)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_48_interval_0.stl')