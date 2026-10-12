import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.31), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.72387, 0.89031)
loop_1 = loop_1.lineTo(0.34566, 0.89127)
loop_1 = loop_1.threePointArc((0.2417, 0.89149), (0.13421, 0.89337))
loop_1 = loop_1.threePointArc((0.0665, 0.89254), (-0.00321, 0.89391))
loop_1 = loop_1.lineTo(-0.1666, 0.89409)
loop_1 = loop_1.lineTo(-0.31194, 0.89473)
loop_1 = loop_1.threePointArc((-0.39958, 0.89683), (-0.483, 0.89738))
loop_1 = loop_1.threePointArc((-0.53665, 0.89902), (-0.5917, 0.90139))
loop_1 = loop_1.lineTo(-0.65934, 0.90357)
loop_1 = loop_1.lineTo(-0.71934, 0.89306)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_73_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_73_interval_1.stl')