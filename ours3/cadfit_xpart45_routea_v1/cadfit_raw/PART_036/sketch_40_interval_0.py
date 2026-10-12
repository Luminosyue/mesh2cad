import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.22, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02764, 0.21273)
loop_1 = loop_1.lineTo(0.04523, 0.20949)
loop_1 = loop_1.lineTo(0.06098, 0.19575)
loop_1 = loop_1.threePointArc((0.06571, 0.18576), (0.06874, 0.17846))
loop_1 = loop_1.lineTo(0.06652, 0.16098)
loop_1 = loop_1.lineTo(0.05352, 0.14574)
loop_1 = loop_1.threePointArc((0.03598, 0.13922), (0.0275, 0.13838))
loop_1 = loop_1.threePointArc((0.02161, 0.14086), (0.01597, 0.143))
loop_1 = loop_1.threePointArc((0.00569, 0.15039), (0.00129, 0.15463))
loop_1 = loop_1.lineTo(-0.00704, 0.17488)
loop_1 = loop_1.threePointArc((-0.0031, 0.18608), (0.00089, 0.19319))
loop_1 = loop_1.threePointArc((0.01898, 0.20748), (0.02757, 0.21268))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.32)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/sketch_40_interval_0.stl')