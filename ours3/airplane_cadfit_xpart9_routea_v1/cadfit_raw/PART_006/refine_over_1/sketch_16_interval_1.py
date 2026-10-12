import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.08376, 0.47525, -0.13608), normal=(-0.02892, 0.96262, -0.26931), xDir=(0.99955, 0.03002, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.24369, -0.12168)
loop_1 = loop_1.lineTo(0.25858, -0.12544)
loop_1 = loop_1.threePointArc((0.27879, -0.13141), (0.29423, -0.1347))
loop_1 = loop_1.lineTo(0.31907, -0.13924)
loop_1 = loop_1.lineTo(0.33311, -0.13921)
loop_1 = loop_1.lineTo(0.35335, -0.13887)
loop_1 = loop_1.threePointArc((0.39873, -0.13652), (0.43981, -0.13483))
loop_1 = loop_1.lineTo(0.49042, -0.13202)
loop_1 = loop_1.threePointArc((0.52392, -0.13038), (0.55134, -0.12793))
loop_1 = loop_1.lineTo(0.56395, -0.12683)
loop_1 = loop_1.lineTo(0.58063, -0.12436)
loop_1 = loop_1.lineTo(0.6007, -0.11871)
loop_1 = loop_1.lineTo(0.62076, -0.11053)
loop_1 = loop_1.lineTo(0.6408, -0.09874)
loop_1 = loop_1.lineTo(0.65643, -0.08864)
loop_1 = loop_1.lineTo(0.22983, -0.12028)
loop_1 = loop_1.lineTo(0.24369, -0.12168)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_16_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_16_interval_1.stl')