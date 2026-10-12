import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43664, 0.15237, -0.22251), normal=(0.00278, -0.00089, 1.0), xDir=(-0.0, 1.0, 0.00089))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17754, 0.25514)
loop_1 = loop_1.lineTo(-0.05578, 0.00335)
loop_1 = loop_1.lineTo(-0.0798, 0.01229)
loop_1 = loop_1.lineTo(-0.1016, 0.0224)
loop_1 = loop_1.lineTo(-0.11364, 0.03026)
loop_1 = loop_1.lineTo(-0.12435, 0.03823)
loop_1 = loop_1.threePointArc((-0.13528, 0.04867), (-0.14643, 0.05979))
loop_1 = loop_1.lineTo(-0.16661, 0.0841)
loop_1 = loop_1.threePointArc((-0.17435, 0.09509), (-0.17998, 0.10365))
loop_1 = loop_1.lineTo(-0.19204, 0.12711)
loop_1 = loop_1.lineTo(-0.19896, 0.14961)
loop_1 = loop_1.threePointArc((-0.20024, 0.16085), (-0.20166, 0.17079))
loop_1 = loop_1.lineTo(-0.19817, 0.19524)
loop_1 = loop_1.lineTo(-0.18857, 0.22241)
loop_1 = loop_1.threePointArc((-0.18334, 0.23873), (-0.17853, 0.25248))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.48)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_3_interval_0.stl')