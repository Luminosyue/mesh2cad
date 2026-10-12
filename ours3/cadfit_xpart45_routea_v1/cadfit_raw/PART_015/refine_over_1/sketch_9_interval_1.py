import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.50759, -0.12273, -0.02976), normal=(0.95324, -0.30222, 0.00027), xDir=(-0.30222, -0.95324, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12193, 0.26829)
loop_1 = loop_1.lineTo(0.12519, 0.24046)
loop_1 = loop_1.lineTo(0.08908, 0.24974)
loop_1 = loop_1.lineTo(0.06577, 0.2517)
loop_1 = loop_1.lineTo(0.04076, 0.25245)
loop_1 = loop_1.lineTo(0.02977, 0.2517)
loop_1 = loop_1.lineTo(0.01874, 0.25006)
loop_1 = loop_1.lineTo(-0.02344, 0.24212)
loop_1 = loop_1.lineTo(-0.03349, 0.24363)
loop_1 = loop_1.lineTo(-0.05792, 0.24328)
loop_1 = loop_1.lineTo(-0.08399, 0.24004)
loop_1 = loop_1.lineTo(-0.09959, 0.24004)
loop_1 = loop_1.threePointArc((-0.0986, 0.24951), (-0.09786, 0.2567))
loop_1 = loop_1.lineTo(0.11948, 0.26816)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.34)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_9_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_9_interval_1.stl')