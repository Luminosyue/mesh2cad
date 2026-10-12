import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.13005, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12826, 0.11492)
loop_1 = loop_1.lineTo(0.62476, 0.11458)
loop_1 = loop_1.threePointArc((0.55617, 0.11234), (0.4907, 0.10939))
loop_1 = loop_1.threePointArc((0.45917, 0.10943), (0.42927, 0.10857))
loop_1 = loop_1.threePointArc((0.38787, 0.10848), (0.34849, 0.10745))
loop_1 = loop_1.lineTo(0.25928, 0.10697)
loop_1 = loop_1.threePointArc((0.22114, 0.1065), (0.18488, 0.1055))
loop_1 = loop_1.threePointArc((0.15581, 0.10557), (0.12826, 0.10489))
loop_1 = loop_1.lineTo(0.12826, 0.11492)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_36_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_36_interval_1.stl')