import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.11321, 0.91405, -0.18014), normal=(0.18177, 0.98334, 3e-05), xDir=(0.98334, -0.18177, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.20124, 0.33968)
loop_1 = loop_1.lineTo(-0.25834, 0.33968)
loop_1 = loop_1.lineTo(-0.25816, 0.1318)
loop_1 = loop_1.lineTo(-0.25482, 0.18137)
loop_1 = loop_1.lineTo(-0.25055, 0.23077)
loop_1 = loop_1.lineTo(-0.23871, 0.27587)
loop_1 = loop_1.threePointArc((-0.22238, 0.30913), (-0.20827, 0.33442))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_12_interval_0.stl')