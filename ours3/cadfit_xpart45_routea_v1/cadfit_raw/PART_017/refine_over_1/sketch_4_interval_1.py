import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06616, -0.43057, 0.01997), normal=(-0.00125, -1.0, -0.00017), xDir=(-1.0, 0.00125, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.21799, 0.49853)
loop_1 = loop_1.lineTo(-0.19338, 0.51231)
loop_1 = loop_1.lineTo(-0.18331, 0.51714)
loop_1 = loop_1.threePointArc((-0.16189, 0.52566), (-0.14377, 0.53253))
loop_1 = loop_1.threePointArc((-0.12269, 0.53878), (-0.10603, 0.54389))
loop_1 = loop_1.threePointArc((-0.08423, 0.54903), (-0.06522, 0.55315))
loop_1 = loop_1.lineTo(-0.02847, 0.55814)
loop_1 = loop_1.lineTo(-0.01712, 0.55858)
loop_1 = loop_1.lineTo(-0.31282, 0.55921)
loop_1 = loop_1.lineTo(-0.31282, 0.42975)
loop_1 = loop_1.lineTo(-0.29616, 0.44477)
loop_1 = loop_1.lineTo(-0.26058, 0.47265)
loop_1 = loop_1.lineTo(-0.23081, 0.49091)
loop_1 = loop_1.lineTo(-0.21799, 0.49853)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_4_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_4_interval_1.stl')