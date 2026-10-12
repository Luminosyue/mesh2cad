import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.4191), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.38466, 0.88374)
loop_1 = loop_1.lineTo(-0.32154, 0.8828)
loop_1 = loop_1.lineTo(-0.29455, 0.88167)
loop_1 = loop_1.threePointArc((-0.28633, 0.87935), (-0.27858, 0.87755))
loop_1 = loop_1.threePointArc((-0.26843, 0.87489), (-0.2582, 0.87184))
loop_1 = loop_1.lineTo(-0.22135, 0.84536)
loop_1 = loop_1.lineTo(-0.18906, 0.8046)
loop_1 = loop_1.lineTo(-0.16659, 0.76994)
loop_1 = loop_1.threePointArc((-0.15893, 0.76298), (-0.15154, 0.75672))
loop_1 = loop_1.lineTo(-0.11725, 0.75085)
loop_1 = loop_1.lineTo(-0.11166, 0.8844)
loop_1 = loop_1.lineTo(-0.38441, 0.88374)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_45_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_45_interval_1.stl')