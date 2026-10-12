import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.92926, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30316, 0.99711)
loop_1 = loop_1.threePointArc((0.33747, 0.99271), (0.37107, 0.97969))
loop_1 = loop_1.threePointArc((0.38288, 0.96954), (0.39235, 0.95908))
loop_1 = loop_1.threePointArc((0.4068, 0.93551), (0.41443, 0.91003))
loop_1 = loop_1.threePointArc((0.44382, 0.66073), (0.46852, 0.40243))
loop_1 = loop_1.lineTo(0.58907, -0.74519)
loop_1 = loop_1.threePointArc((0.59141, -0.78269), (0.59055, -0.81969))
loop_1 = loop_1.threePointArc((0.58297, -0.84888), (0.56911, -0.87471))
loop_1 = loop_1.lineTo(0.54675, -0.89923)
loop_1 = loop_1.threePointArc((0.50764, -0.91679), (0.46536, -0.92244))
loop_1 = loop_1.lineTo(-0.01173, -0.96622)
loop_1 = loop_1.lineTo(-0.27564, -0.99075)
loop_1 = loop_1.threePointArc((-0.33474, -0.9738), (-0.37618, -0.92786))
loop_1 = loop_1.threePointArc((-0.3837, -0.91401), (-0.38713, -0.90023))
loop_1 = loop_1.threePointArc((-0.39566, -0.85218), (-0.39994, -0.80353))
loop_1 = loop_1.lineTo(-0.48805, 0.03601)
loop_1 = loop_1.threePointArc((-0.5278, 0.40851), (-0.56609, 0.79468))
loop_1 = loop_1.threePointArc((-0.5656, 0.81584), (-0.56139, 0.83539))
loop_1 = loop_1.threePointArc((-0.55029, 0.86246), (-0.53522, 0.88619))
loop_1 = loop_1.threePointArc((-0.52549, 0.89561), (-0.51531, 0.90165))
loop_1 = loop_1.threePointArc((-0.50174, 0.9097), (-0.48815, 0.91393))
loop_1 = loop_1.threePointArc((-0.43029, 0.92475), (-0.37105, 0.9282))
loop_1 = loop_1.threePointArc((-0.34931, 0.92854), (-0.32955, 0.92307))
loop_1 = loop_1.lineTo(-0.30333, 0.90558)
loop_1 = loop_1.lineTo(-0.28349, 0.88546)
loop_1 = loop_1.threePointArc((-0.27196, 0.86942), (-0.26336, 0.85303))
loop_1 = loop_1.lineTo(-0.25991, 0.83209)
loop_1 = loop_1.threePointArc((-0.26938, 0.80298), (-0.27633, 0.77648))
loop_1 = loop_1.threePointArc((-0.27495, 0.7645), (-0.27391, 0.75515))
loop_1 = loop_1.lineTo(-0.25904, 0.74095)
loop_1 = loop_1.threePointArc((-0.11957, 0.72137), (0.02268, 0.69593))
loop_1 = loop_1.lineTo(0.05352, 0.69356)
loop_1 = loop_1.lineTo(0.07304, 0.69734)
loop_1 = loop_1.threePointArc((0.08066, 0.70793), (0.08414, 0.71786))
loop_1 = loop_1.threePointArc((0.06914, 0.76173), (0.05211, 0.80051))
loop_1 = loop_1.lineTo(0.04555, 0.82271)
loop_1 = loop_1.threePointArc((0.04517, 0.84727), (0.04752, 0.87031))
loop_1 = loop_1.threePointArc((0.04769, 0.88535), (0.04676, 0.8976))
loop_1 = loop_1.threePointArc((0.05297, 0.91295), (0.05946, 0.92643))
loop_1 = loop_1.lineTo(0.08195, 0.95504)
loop_1 = loop_1.threePointArc((0.09547, 0.96605), (0.10615, 0.97637))
loop_1 = loop_1.lineTo(0.11787, 0.97808)
loop_1 = loop_1.lineTo(0.15699, 0.9831)
loop_1 = loop_1.lineTo(0.30121, 0.99729)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.84)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/robot_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_006/PART_006.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/robot_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_006/PART_006_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
