import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.2, 0.12871, -0.09914), normal=(0.00024, 0.01364, -0.99991), xDir=(0.0, -0.99991, -0.01364))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.55669, -0.24005)
loop_1 = loop_1.threePointArc((-0.57757, -0.23648), (-0.59763, -0.23318))
loop_1 = loop_1.lineTo(-0.63159, -0.21652)
loop_1 = loop_1.lineTo(-0.64508, -0.21077)
loop_1 = loop_1.lineTo(-0.69107, -0.19838)
loop_1 = loop_1.lineTo(-0.7398, -0.18938)
loop_1 = loop_1.lineTo(-0.7845, -0.18314)
loop_1 = loop_1.lineTo(-0.82852, -0.18971)
loop_1 = loop_1.lineTo(-0.78239, -0.17953)
loop_1 = loop_1.lineTo(-0.73051, -0.18691)
loop_1 = loop_1.lineTo(-0.68138, -0.19589)
loop_1 = loop_1.lineTo(-0.63531, -0.20608)
loop_1 = loop_1.lineTo(-0.60591, -0.21732)
loop_1 = loop_1.lineTo(-0.57881, -0.22912)
loop_1 = loop_1.lineTo(-0.55693, -0.2399)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_11_interval_0.stl')