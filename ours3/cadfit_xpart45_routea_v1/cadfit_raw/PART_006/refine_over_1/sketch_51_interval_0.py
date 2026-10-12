import cadquery as cq
import math

plane_1 = cq.Plane(origin=(1.00969, -0.31625, 0.02623), normal=(-0.95467, 0.29756, -0.0085), xDir=(0.29757, 0.9547, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17471, -0.02886)
loop_1 = loop_1.lineTo(-0.16091, -0.03429)
loop_1 = loop_1.threePointArc((-0.11421, -0.05033), (-0.06887, -0.06417))
loop_1 = loop_1.lineTo(-0.03391, -0.08404)
loop_1 = loop_1.lineTo(-0.01979, -0.13649)
loop_1 = loop_1.lineTo(-0.01534, -0.44117)
loop_1 = loop_1.lineTo(-0.0224, -0.46227)
loop_1 = loop_1.lineTo(-0.03283, -0.48325)
loop_1 = loop_1.lineTo(-0.04659, -0.50405)
loop_1 = loop_1.threePointArc((-0.11077, -0.52243), (-0.17606, -0.5404))
loop_1 = loop_1.lineTo(-0.17472, -0.0305)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_51_interval_0.stl')