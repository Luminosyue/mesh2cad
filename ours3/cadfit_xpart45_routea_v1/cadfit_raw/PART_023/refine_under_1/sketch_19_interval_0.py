import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0078, -0.12451, 0.00977), normal=(0.55682, -0.83063, 0.00124), xDir=(-0.83063, -0.55682, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.58225, -0.36012)
loop_1 = loop_1.threePointArc((-0.58235, -0.42246), (-0.58237, -0.4823))
loop_1 = loop_1.threePointArc((-0.58724, -0.47288), (-0.59161, -0.46425))
loop_1 = loop_1.lineTo(-0.5993, -0.44327)
loop_1 = loop_1.lineTo(-0.60305, -0.42144)
loop_1 = loop_1.lineTo(-0.60475, -0.40724)
loop_1 = loop_1.lineTo(-0.60158, -0.39458)
loop_1 = loop_1.lineTo(-0.59382, -0.38175)
loop_1 = loop_1.threePointArc((-0.58581, -0.36726), (-0.58286, -0.36133))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_19_interval_0.stl')