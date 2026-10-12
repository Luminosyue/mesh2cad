import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.61679, 0.0473, 0.36561), normal=(-0.79983, -0.01226, 0.6001), xDir=(-0.01533, 0.99988, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32292, -0.10951)
loop_1 = loop_1.lineTo(0.3028, 0.32553)
loop_1 = loop_1.lineTo(0.37465, 0.32446)
loop_1 = loop_1.lineTo(0.36872, -0.32028)
loop_1 = loop_1.lineTo(0.24812, -0.31984)
loop_1 = loop_1.lineTo(0.26949, -0.31308)
loop_1 = loop_1.lineTo(0.28736, -0.30242)
loop_1 = loop_1.lineTo(0.3069, -0.28327)
loop_1 = loop_1.lineTo(0.32839, -0.24275)
loop_1 = loop_1.threePointArc((0.33283, -0.2145), (0.33528, -0.19218))
loop_1 = loop_1.threePointArc((0.33054, -0.15568), (0.32608, -0.13029))
loop_1 = loop_1.lineTo(0.33025, -0.1097)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_22_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_22_interval_1.stl')