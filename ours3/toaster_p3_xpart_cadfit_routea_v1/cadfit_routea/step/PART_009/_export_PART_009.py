import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.1316), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.03625, 0.0061)
loop_1 = loop_1.circle(0.02358)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.12), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.77436, -0.005)
loop_1 = loop_1.circle(0.01811)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.13)
plane_3 = cq.Plane(origin=(-0.0338, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_3 = cq.Workplane(plane_3)
loop_1 = sketch_3.moveTo(0.97963, 0.07409)
loop_1 = loop_1.threePointArc((0.99075, 0.06435), (0.99324, 0.06036))
loop_1 = loop_1.lineTo(0.97107, 0.03352)
loop_1 = loop_1.lineTo(0.9533, 0.03395)
loop_1 = loop_1.lineTo(0.93396, 0.0507)
loop_1 = loop_1.lineTo(0.94378, 0.069)
loop_1 = loop_1.lineTo(0.97963, 0.07409)
loop_1 = loop_1.close()
sketch_3=sketch_3.add(loop_1)
solid_3 = sketch_3.extrude(0.07)
plane_4 = cq.Plane(origin=(0.0, -0.99, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_4 = cq.Workplane(plane_4)
loop_1 = sketch_4.moveTo(0.01332, 0.05434)
loop_1 = loop_1.circle(0.02734)
sketch_4=sketch_4.add(loop_1)
solid_4 = sketch_4.extrude(1.99)

result = solid_1
result = result.add(solid_2)
result = result.add(solid_3)
result = result.add(solid_4)

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_009/PART_009.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_009/PART_009_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
