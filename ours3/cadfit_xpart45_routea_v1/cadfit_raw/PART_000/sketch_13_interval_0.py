import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00204, 0.07768, -0.04158), normal=(0.00621, 0.00056, 0.99998), xDir=(0.0, 1.0, -0.00056))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.91555, -0.0195)
loop_1 = loop_1.threePointArc((-0.90515, -0.01998), (-0.89516, -0.02029))
loop_1 = loop_1.lineTo(-0.88205, -0.01761)
loop_1 = loop_1.lineTo(-0.89733, 0.02137)
loop_1 = loop_1.threePointArc((-0.90753, 0.0205), (-0.91816, 0.01984))
loop_1 = loop_1.lineTo(-0.98939, 0.03771)
loop_1 = loop_1.threePointArc((-1.00058, 0.0367), (-1.01226, 0.03593))
loop_1 = loop_1.lineTo(-1.07529, 0.0054)
loop_1 = loop_1.threePointArc((-1.07539, -0.00444), (-1.07532, -0.01389))
loop_1 = loop_1.lineTo(-1.05518, -0.03962)
loop_1 = loop_1.lineTo(-1.04467, -0.03761)
loop_1 = loop_1.lineTo(-1.03317, -0.03571)
loop_1 = loop_1.lineTo(-1.00779, -0.03593)
loop_1 = loop_1.threePointArc((-1.00115, -0.03638), (-0.99477, -0.03671))
loop_1 = loop_1.lineTo(-0.91555, -0.0195)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_13_interval_0.stl')