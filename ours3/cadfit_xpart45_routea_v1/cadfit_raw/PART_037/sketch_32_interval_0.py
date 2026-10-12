import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.05, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.61628, 0.00299)
loop_1 = loop_1.lineTo(-0.62421, -0.01691)
loop_1 = loop_1.threePointArc((-0.62238, -0.02502), (-0.62037, -0.03199))
loop_1 = loop_1.lineTo(-0.60589, -0.04487)
loop_1 = loop_1.lineTo(-0.58866, -0.04667)
loop_1 = loop_1.lineTo(-0.57511, -0.03648)
loop_1 = loop_1.threePointArc((-0.56999, -0.02583), (-0.56814, -0.02013))
loop_1 = loop_1.lineTo(-0.57034, -0.00453)
loop_1 = loop_1.lineTo(-0.58631, 0.00451)
loop_1 = loop_1.lineTo(-0.61628, 0.00299)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_32_interval_0.stl')