import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.19), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.91719, 0.00095)
loop_1 = loop_1.threePointArc((0.91805, -0.00521), (0.919, -0.01111))
loop_1 = loop_1.threePointArc((0.92124, -0.01678), (0.92329, -0.02265))
loop_1 = loop_1.lineTo(0.931, -0.0342)
loop_1 = loop_1.threePointArc((0.94449, -0.04356), (0.95008, -0.04623))
loop_1 = loop_1.threePointArc((0.95687, -0.04914), (0.96374, -0.05233))
loop_1 = loop_1.lineTo(0.97423, -0.05767)
loop_1 = loop_1.threePointArc((0.97999, -0.05955), (0.98544, -0.06123))
loop_1 = loop_1.lineTo(0.9971, -0.05172)
loop_1 = loop_1.lineTo(0.99941, -0.01643)
loop_1 = loop_1.threePointArc((0.99943, 0.00016), (0.9992, 0.01598))
loop_1 = loop_1.lineTo(0.99913, 0.03938)
loop_1 = loop_1.lineTo(0.99681, 0.05184)
loop_1 = loop_1.lineTo(0.98514, 0.05989)
loop_1 = loop_1.lineTo(0.97322, 0.05548)
loop_1 = loop_1.threePointArc((0.96157, 0.04938), (0.94942, 0.0433))
loop_1 = loop_1.threePointArc((0.94406, 0.04039), (0.93849, 0.03757))
loop_1 = loop_1.threePointArc((0.93055, 0.02918), (0.92671, 0.0247))
loop_1 = loop_1.threePointArc((0.92343, 0.01829), (0.92043, 0.01219))
loop_1 = loop_1.threePointArc((0.91889, 0.00666), (0.91719, 0.00106))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)
plane_2 = cq.Plane(origin=(0.0, -0.99, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.00251, 0.13329)
loop_1 = loop_1.circle(0.05812)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.97)

result = solid_1
result = result.add(solid_2)

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_015/PART_015.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_015/PART_015_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
