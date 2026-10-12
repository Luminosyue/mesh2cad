import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.97236, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02471, -0.16808)
loop_1 = loop_1.threePointArc((-0.02959, -0.17848), (-0.03494, -0.18918))
loop_1 = loop_1.threePointArc((-0.04886, -0.21729), (-0.06383, -0.24616))
loop_1 = loop_1.lineTo(-0.08219, -0.27873)
loop_1 = loop_1.lineTo(-0.09113, -0.29331)
loop_1 = loop_1.lineTo(-0.1022, -0.30964)
loop_1 = loop_1.lineTo(-0.12397, -0.33321)
loop_1 = loop_1.lineTo(-0.02471, -0.33299)
loop_1 = loop_1.lineTo(-0.02471, -0.16823)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.45)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_27_interval_0.stl')