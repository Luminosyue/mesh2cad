import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.73634, 0.18493, -0.0252), normal=(-0.96225, 0.27216, 0.00118), xDir=(0.27216, 0.96225, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.43089, 0.17718)
loop_1 = loop_1.lineTo(-0.42977, -0.18061)
loop_1 = loop_1.lineTo(-0.43844, -0.16912)
loop_1 = loop_1.threePointArc((-0.44092, -0.14728), (-0.44309, -0.12449))
loop_1 = loop_1.threePointArc((-0.44154, -0.09909), (-0.43974, -0.07639))
loop_1 = loop_1.threePointArc((-0.44325, -0.02557), (-0.44686, 0.01982))
loop_1 = loop_1.threePointArc((-0.4457, 0.04516), (-0.4447, 0.06793))
loop_1 = loop_1.lineTo(-0.4457, 0.10269)
loop_1 = loop_1.lineTo(-0.44746, 0.11603)
loop_1 = loop_1.lineTo(-0.44031, 0.14987)
loop_1 = loop_1.lineTo(-0.43817, 0.16414)
loop_1 = loop_1.lineTo(-0.43221, 0.17481)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_8_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_8_interval_1.stl')