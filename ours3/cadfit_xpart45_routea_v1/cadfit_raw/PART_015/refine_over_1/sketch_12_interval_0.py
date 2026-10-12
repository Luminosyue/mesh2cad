import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45356, -0.75944, -0.0287), normal=(0.65793, 0.75308, -0.00279), xDir=(0.75308, -0.65793, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1334, 0.26018)
loop_1 = loop_1.threePointArc((-0.12581, 0.25942), (-0.11851, 0.25889))
loop_1 = loop_1.lineTo(-0.10395, 0.25777)
loop_1 = loop_1.lineTo(-0.08958, 0.25414)
loop_1 = loop_1.lineTo(-0.07649, 0.25039)
loop_1 = loop_1.lineTo(-0.06361, 0.24624)
loop_1 = loop_1.lineTo(-0.0509, 0.24168)
loop_1 = loop_1.lineTo(-0.03863, 0.23681)
loop_1 = loop_1.lineTo(-0.04905, 0.23444)
loop_1 = loop_1.lineTo(-0.07074, 0.2386)
loop_1 = loop_1.lineTo(-0.10609, 0.24202)
loop_1 = loop_1.lineTo(-0.12009, 0.24594)
loop_1 = loop_1.lineTo(-0.13344, 0.24419)
loop_1 = loop_1.lineTo(-0.1334, 0.25907)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.63)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_12_interval_0.stl')