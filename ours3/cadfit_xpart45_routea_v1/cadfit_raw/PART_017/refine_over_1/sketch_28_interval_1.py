import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01616, 0.11223, 0.66415), normal=(-0.0004, 0.04126, 0.99915), xDir=(0.0, 0.99915, -0.04126))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17807, 0.25569)
loop_1 = loop_1.lineTo(0.2202, 0.25916)
loop_1 = loop_1.lineTo(0.22003, 0.03613)
loop_1 = loop_1.lineTo(0.21675, 0.07656)
loop_1 = loop_1.threePointArc((0.21458, 0.08912), (0.2123, 0.10086))
loop_1 = loop_1.lineTo(0.20941, 0.11678)
loop_1 = loop_1.threePointArc((0.20612, 0.13643), (0.20344, 0.15205))
loop_1 = loop_1.lineTo(0.1942, 0.19159)
loop_1 = loop_1.lineTo(0.17863, 0.23029)
loop_1 = loop_1.lineTo(0.12612, 0.25022)
loop_1 = loop_1.lineTo(0.10875, 0.25004)
loop_1 = loop_1.lineTo(0.17807, 0.25618)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_28_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_28_interval_1.stl')