import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.60495, 0.67764, -0.07695), normal=(-0.66585, 0.74608, -0.00024), xDir=(0.74608, 0.66585, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31274, 0.44287)
loop_1 = loop_1.lineTo(-0.31254, 0.27648)
loop_1 = loop_1.lineTo(-0.30918, 0.31819)
loop_1 = loop_1.lineTo(-0.30826, 0.33594)
loop_1 = loop_1.threePointArc((-0.30618, 0.36234), (-0.3045, 0.38579))
loop_1 = loop_1.threePointArc((-0.29945, 0.3952), (-0.29503, 0.40328))
loop_1 = loop_1.lineTo(-0.28045, 0.43763)
loop_1 = loop_1.lineTo(-0.31095, 0.44287)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_33_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_33_interval_1.stl')