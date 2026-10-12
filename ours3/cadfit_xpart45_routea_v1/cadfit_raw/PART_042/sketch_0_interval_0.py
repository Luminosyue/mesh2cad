import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.09103, 0.28416, 0.00229), normal=(0.02355, -0.99972, -0.0022), xDir=(-0.99972, -0.02355, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.63333, 0.07855)
loop_1 = loop_1.lineTo(-0.62192, 0.07567)
loop_1 = loop_1.lineTo(-0.60722, 0.06298)
loop_1 = loop_1.lineTo(-0.59816, 0.04261)
loop_1 = loop_1.lineTo(-0.5984, 0.01379)
loop_1 = loop_1.lineTo(-0.60434, 0.0015)
loop_1 = loop_1.lineTo(-0.61701, -0.01182)
loop_1 = loop_1.threePointArc((-0.62434, -0.01441), (-0.63006, -0.01651))
loop_1 = loop_1.lineTo(-0.64245, -0.01662)
loop_1 = loop_1.lineTo(-0.66257, -0.00912)
loop_1 = loop_1.threePointArc((-0.66871, -0.00162), (-0.67463, 0.00554))
loop_1 = loop_1.lineTo(-0.67704, 0.0281)
loop_1 = loop_1.lineTo(-0.67525, 0.04602)
loop_1 = loop_1.lineTo(-0.66888, 0.05856)
loop_1 = loop_1.lineTo(-0.65789, 0.0716)
loop_1 = loop_1.lineTo(-0.64733, 0.07745)
loop_1 = loop_1.lineTo(-0.63333, 0.07855)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_0_interval_0.stl')