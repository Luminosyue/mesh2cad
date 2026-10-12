import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.6933, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.3129, 0.67668)
loop_1 = loop_1.lineTo(0.29472, 0.67441)
loop_1 = loop_1.threePointArc((0.28563, 0.67093), (0.27715, 0.66746))
loop_1 = loop_1.lineTo(0.25857, 0.66037)
loop_1 = loop_1.lineTo(0.22179, 0.6204)
loop_1 = loop_1.lineTo(0.21138, 0.60367)
loop_1 = loop_1.lineTo(0.19563, 0.58209)
loop_1 = loop_1.threePointArc((0.19089, 0.57645), (0.18583, 0.57095))
loop_1 = loop_1.threePointArc((0.17696, 0.56857), (0.16882, 0.56578))
loop_1 = loop_1.lineTo(0.14915, 0.55938)
loop_1 = loop_1.threePointArc((0.13058, 0.56056), (0.11145, 0.56204))
loop_1 = loop_1.lineTo(0.10943, 0.67648)
loop_1 = loop_1.lineTo(0.31271, 0.67668)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_35_interval_0.stl')