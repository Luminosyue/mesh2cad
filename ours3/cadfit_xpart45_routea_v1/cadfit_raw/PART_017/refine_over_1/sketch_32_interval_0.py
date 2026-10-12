import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03962, -0.40374, -0.74973), normal=(1e-05, 0.95255, -0.30437), xDir=(1.0, -1e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01845, 0.14933)
loop_1 = loop_1.lineTo(0.00103, 0.13472)
loop_1 = loop_1.threePointArc((0.02212, 0.12579), (0.03927, 0.11826))
loop_1 = loop_1.threePointArc((0.05751, 0.10847), (0.07202, 0.10152))
loop_1 = loop_1.threePointArc((0.08914, 0.093), (0.10222, 0.0863))
loop_1 = loop_1.threePointArc((0.11972, 0.07949), (0.13364, 0.07324))
loop_1 = loop_1.threePointArc((0.15456, 0.06259), (0.17223, 0.05317))
loop_1 = loop_1.lineTo(0.20598, 0.03715)
loop_1 = loop_1.threePointArc((0.21917, 0.03041), (0.23016, 0.02446))
loop_1 = loop_1.lineTo(0.24953, 0.01427)
loop_1 = loop_1.lineTo(0.28951, -0.00342)
loop_1 = loop_1.lineTo(0.30747, -0.01508)
loop_1 = loop_1.lineTo(0.3268, -0.0256)
loop_1 = loop_1.lineTo(0.34038, -0.03223)
loop_1 = loop_1.lineTo(0.34035, 0.1523)
loop_1 = loop_1.lineTo(-0.02188, 0.1523)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_32_interval_0.stl')