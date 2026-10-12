import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05354, -0.01835, -0.23452), normal=(0.00848, -0.04584, 0.99891), xDir=(-0.0, 0.99895, 0.04584))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.58944, -0.49964)
loop_1 = loop_1.lineTo(0.65756, -0.49964)
loop_1 = loop_1.lineTo(0.65714, -0.40688)
loop_1 = loop_1.lineTo(0.63439, -0.4425)
loop_1 = loop_1.lineTo(0.61739, -0.46462)
loop_1 = loop_1.lineTo(0.6022, -0.48329)
loop_1 = loop_1.lineTo(0.59029, -0.49855)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.54)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_9_interval_0.stl')