import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.37371, -0.2161, -0.03364), normal=(0.92728, -0.37435, 0.00299), xDir=(-0.37435, -0.92729, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28136, 0.0698)
loop_1 = loop_1.lineTo(0.2796, 0.04835)
loop_1 = loop_1.lineTo(0.26846, 0.03278)
loop_1 = loop_1.threePointArc((0.25728, 0.02676), (0.24586, 0.02084))
loop_1 = loop_1.lineTo(0.24282, 0.2413)
loop_1 = loop_1.lineTo(0.28408, 0.19471)
loop_1 = loop_1.lineTo(0.28058, 0.18457)
loop_1 = loop_1.lineTo(0.28022, 0.16031)
loop_1 = loop_1.lineTo(0.2812, 0.13787)
loop_1 = loop_1.threePointArc((0.28096, 0.10194), (0.2814, 0.06987))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.4)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_9_interval_3.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_9_interval_3.stl')