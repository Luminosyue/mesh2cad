import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.15347), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.87457, -0.46554)
loop_1 = loop_1.lineTo(-0.86118, -0.48458)
loop_1 = loop_1.lineTo(-0.84857, -0.50236)
loop_1 = loop_1.lineTo(-0.8637, -0.48127)
loop_1 = loop_1.lineTo(-0.82689, -0.53464)
loop_1 = loop_1.threePointArc((-0.81941, -0.54604), (-0.81218, -0.5568))
loop_1 = loop_1.lineTo(-0.87465, -0.55718)
loop_1 = loop_1.lineTo(-0.87442, -0.46686)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_64_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_64_interval_0.stl')