import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.98), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1443, -0.01454)
loop_1 = loop_1.lineTo(-0.14345, -0.02542)
loop_1 = loop_1.lineTo(-0.13322, -0.03444)
loop_1 = loop_1.threePointArc((-0.1273, -0.03576), (-0.12172, -0.03671))
loop_1 = loop_1.threePointArc((-0.10534, -0.03684), (-0.0898, -0.03676))
loop_1 = loop_1.threePointArc((-0.03545, -0.03689), (0.01654, -0.03669))
loop_1 = loop_1.lineTo(0.04543, -0.03694)
loop_1 = loop_1.threePointArc((0.05384, -0.03712), (0.06174, -0.03693))
loop_1 = loop_1.lineTo(0.07931, -0.02512)
loop_1 = loop_1.threePointArc((0.07949, -0.019), (0.07949, -0.01329))
loop_1 = loop_1.lineTo(0.0737, 0.00738)
loop_1 = loop_1.threePointArc((0.06625, 0.01634), (0.05886, 0.02453))
loop_1 = loop_1.lineTo(0.04885, 0.03206)
loop_1 = loop_1.lineTo(0.03806, 0.03482)
loop_1 = loop_1.threePointArc((0.02746, 0.03547), (0.01744, 0.03549))
loop_1 = loop_1.threePointArc((-0.00293, 0.0355), (-0.02397, 0.0357))
loop_1 = loop_1.lineTo(-0.08386, 0.03617)
loop_1 = loop_1.threePointArc((-0.0932, 0.03602), (-0.10198, 0.03564))
loop_1 = loop_1.lineTo(-0.11235, 0.03364)
loop_1 = loop_1.lineTo(-0.12254, 0.02781)
loop_1 = loop_1.lineTo(-0.13287, 0.01702)
loop_1 = loop_1.lineTo(-0.13882, 0.00648)
loop_1 = loop_1.lineTo(-0.14257, -0.00465)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_038/PART_038.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_038/PART_038_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
