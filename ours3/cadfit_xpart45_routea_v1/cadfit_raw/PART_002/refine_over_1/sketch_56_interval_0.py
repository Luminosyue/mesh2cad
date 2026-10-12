import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.30885, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28269, -0.50231)
loop_1 = loop_1.threePointArc((-0.27971, -0.51902), (-0.27633, -0.53496))
loop_1 = loop_1.lineTo(-0.27445, -0.54508)
loop_1 = loop_1.threePointArc((-0.27284, -0.56799), (-0.27208, -0.5919))
loop_1 = loop_1.lineTo(-0.27174, -0.61882)
loop_1 = loop_1.lineTo(-0.2627, -0.65517)
loop_1 = loop_1.lineTo(-0.24365, -0.67834)
loop_1 = loop_1.lineTo(-0.22533, -0.69649)
loop_1 = loop_1.lineTo(-0.20652, -0.71454)
loop_1 = loop_1.threePointArc((-0.19936, -0.72261), (-0.19246, -0.73113))
loop_1 = loop_1.lineTo(-0.16736, -0.76684)
loop_1 = loop_1.lineTo(-0.13525, -0.80361)
loop_1 = loop_1.lineTo(-0.28271, -0.80945)
loop_1 = loop_1.lineTo(-0.28271, -0.50259)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.63)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_56_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_56_interval_0.stl')