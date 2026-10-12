import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.79062, 0.29931, -0.10794), normal=(-0.95798, -0.28682, 0.00042), xDir=(-0.28682, 0.95798, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29176, 0.15208)
loop_1 = loop_1.lineTo(0.35872, 0.15208)
loop_1 = loop_1.lineTo(0.35818, -0.20792)
loop_1 = loop_1.lineTo(0.25169, -0.20792)
loop_1 = loop_1.lineTo(0.25161, -0.25287)
loop_1 = loop_1.lineTo(-0.07664, -0.25264)
loop_1 = loop_1.lineTo(-0.07672, -0.20792)
loop_1 = loop_1.lineTo(-0.2919, -0.20792)
loop_1 = loop_1.lineTo(-0.29176, 0.14546)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.65)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_18_interval_0.stl')