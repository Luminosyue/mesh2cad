import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.2), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02583, 0.26304)
loop_1 = loop_1.lineTo(-0.01254, 0.26476)
loop_1 = loop_1.lineTo(0.01559, 0.2646)
loop_1 = loop_1.lineTo(0.03394, 0.26276)
loop_1 = loop_1.lineTo(0.03819, 0.13544)
loop_1 = loop_1.lineTo(-0.00166, 0.16002)
loop_1 = loop_1.lineTo(-0.00938, 0.19921)
loop_1 = loop_1.lineTo(-0.01295, 0.20983)
loop_1 = loop_1.threePointArc((-0.0153, 0.21562), (-0.01778, 0.22108))
loop_1 = loop_1.lineTo(-0.02623, 0.23273)
loop_1 = loop_1.lineTo(-0.02653, 0.24339)
loop_1 = loop_1.lineTo(-0.02575, 0.26113)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_69_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_69_interval_0.stl')