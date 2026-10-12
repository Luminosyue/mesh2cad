import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00383, -0.84545, -0.02132), normal=(-0.0171, 0.8657, -0.50027), xDir=(0.99981, 0.01975, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02425, 0.09081)
loop_1 = loop_1.lineTo(0.03474, 0.08664)
loop_1 = loop_1.lineTo(0.03913, 0.07589)
loop_1 = loop_1.lineTo(0.04001, 0.06383)
loop_1 = loop_1.threePointArc((0.04223, 0.00683), (0.04336, -0.0479))
loop_1 = loop_1.lineTo(0.04413, -0.07567)
loop_1 = loop_1.lineTo(-0.04962, -0.07806)
loop_1 = loop_1.threePointArc((-0.0497, -0.0672), (-0.05007, -0.05679))
loop_1 = loop_1.threePointArc((-0.05042, -0.03448), (-0.05055, -0.01408))
loop_1 = loop_1.lineTo(-0.05078, 0.02764)
loop_1 = loop_1.lineTo(-0.05166, 0.0666)
loop_1 = loop_1.lineTo(-0.02601, 0.08972)
loop_1 = loop_1.threePointArc((-0.01376, 0.08986), (-0.002, 0.09031))
loop_1 = loop_1.lineTo(0.01686, 0.0908)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/greedy_greedy_step_extrude.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/greedy_greedy_step_extrude.stl')