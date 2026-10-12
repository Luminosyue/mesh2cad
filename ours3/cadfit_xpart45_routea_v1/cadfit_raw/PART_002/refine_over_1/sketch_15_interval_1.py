import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.14265, -0.1247, -0.93116), normal=(0.05995, 0.00015, -0.9982), xDir=(0.0, -1.0, -0.00015))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14668, 0.39396)
loop_1 = loop_1.lineTo(-0.16075, 0.37442)
loop_1 = loop_1.lineTo(-0.17894, 0.34764)
loop_1 = loop_1.threePointArc((-0.1885, 0.33102), (-0.19612, 0.31747))
loop_1 = loop_1.lineTo(-0.20741, 0.30025)
loop_1 = loop_1.lineTo(-0.21596, 0.28343)
loop_1 = loop_1.threePointArc((-0.22486, 0.26098), (-0.23187, 0.24205))
loop_1 = loop_1.threePointArc((-0.23877, 0.21936), (-0.24363, 0.19986))
loop_1 = loop_1.lineTo(-0.24672, 0.1861)
loop_1 = loop_1.lineTo(-0.25106, 0.15654)
loop_1 = loop_1.lineTo(-0.23512, 0.34024)
loop_1 = loop_1.lineTo(-0.23007, 0.39396)
loop_1 = loop_1.lineTo(-0.14958, 0.39396)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_15_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_15_interval_1.stl')