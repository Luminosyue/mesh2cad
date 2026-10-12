import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01873, 0.15258, -0.00322), normal=(-0.01606, 0.98078, -0.19446), xDir=(0.99987, 0.01637, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35067, -0.07528)
loop_1 = loop_1.lineTo(-0.40148, -0.07903)
loop_1 = loop_1.lineTo(-0.48195, -0.08368)
loop_1 = loop_1.lineTo(-0.50206, -0.08727)
loop_1 = loop_1.lineTo(-0.54635, -0.09909)
loop_1 = loop_1.lineTo(0.73915, -0.09909)
loop_1 = loop_1.threePointArc((0.75207, -0.05495), (0.76278, -0.01498))
loop_1 = loop_1.lineTo(-0.34883, -0.07517)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_19_interval_0.stl')