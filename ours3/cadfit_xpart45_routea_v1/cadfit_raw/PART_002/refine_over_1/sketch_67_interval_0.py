import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.32939, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.27912, -0.50054)
loop_1 = loop_1.threePointArc((-0.27373, -0.52462), (-0.26824, -0.54768))
loop_1 = loop_1.lineTo(-0.2606, -0.58471)
loop_1 = loop_1.threePointArc((-0.25633, -0.60224), (-0.25204, -0.61876))
loop_1 = loop_1.threePointArc((-0.24635, -0.63053), (-0.24117, -0.64278))
loop_1 = loop_1.threePointArc((-0.23777, -0.64951), (-0.23448, -0.65565))
loop_1 = loop_1.threePointArc((-0.21839, -0.6761), (-0.20284, -0.6953))
loop_1 = loop_1.threePointArc((-0.19289, -0.70872), (-0.18284, -0.72089))
loop_1 = loop_1.lineTo(-0.16364, -0.74805)
loop_1 = loop_1.threePointArc((-0.15333, -0.76564), (-0.14307, -0.78201))
loop_1 = loop_1.lineTo(-0.13113, -0.80319)
loop_1 = loop_1.lineTo(-0.27916, -0.80945)
loop_1 = loop_1.lineTo(-0.27916, -0.50082)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.66)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_67_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_67_interval_0.stl')