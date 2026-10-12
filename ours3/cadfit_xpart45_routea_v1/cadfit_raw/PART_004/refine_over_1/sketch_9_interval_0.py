import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03397, 0.30829, -0.21551), normal=(0.01246, -0.99992, -0.00166), xDir=(-0.99992, -0.01246, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29781, 0.59963)
loop_1 = loop_1.lineTo(-0.32986, 0.59802)
loop_1 = loop_1.lineTo(-0.29778, 0.59886)
loop_1 = loop_1.lineTo(-0.26883, 0.58241)
loop_1 = loop_1.lineTo(-0.22271, 0.54264)
loop_1 = loop_1.lineTo(-0.20983, 0.54576)
loop_1 = loop_1.threePointArc((-0.20253, 0.54651), (-0.1949, 0.54694))
loop_1 = loop_1.lineTo(-0.17626, 0.55649)
loop_1 = loop_1.lineTo(-0.1395, 0.56777)
loop_1 = loop_1.lineTo(-0.13396, 0.58365)
loop_1 = loop_1.lineTo(-0.27065, 0.5837)
loop_1 = loop_1.lineTo(-0.28137, 0.58923)
loop_1 = loop_1.lineTo(-0.29781, 0.59963)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.56)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_9_interval_0.stl')