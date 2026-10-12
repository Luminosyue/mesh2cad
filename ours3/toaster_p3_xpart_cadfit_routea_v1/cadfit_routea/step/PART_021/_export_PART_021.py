import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.95), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1271, 0.01993)
loop_1 = loop_1.lineTo(-0.12554, 0.00917)
loop_1 = loop_1.lineTo(-0.11034, -0.00464)
loop_1 = loop_1.threePointArc((-0.10503, -0.00617), (-0.09961, -0.00807))
loop_1 = loop_1.threePointArc((-0.08458, -0.02187), (-0.07925, -0.02988))
loop_1 = loop_1.lineTo(-0.06883, -0.03868)
loop_1 = loop_1.lineTo(-0.05841, -0.04255)
loop_1 = loop_1.lineTo(-0.04718, -0.04344)
loop_1 = loop_1.lineTo(-0.01688, -0.04348)
loop_1 = loop_1.threePointArc((0.01017, -0.04339), (0.03816, -0.0436))
loop_1 = loop_1.lineTo(0.06173, -0.04363)
loop_1 = loop_1.lineTo(0.07187, -0.04282)
loop_1 = loop_1.lineTo(0.08738, -0.03643)
loop_1 = loop_1.lineTo(0.09932, -0.02035)
loop_1 = loop_1.lineTo(0.11887, -0.00105)
loop_1 = loop_1.threePointArc((0.12146, 0.00456), (0.12366, 0.00988))
loop_1 = loop_1.lineTo(0.12388, 0.02029)
loop_1 = loop_1.lineTo(0.1191, 0.03077)
loop_1 = loop_1.lineTo(0.10743, 0.03938)
loop_1 = loop_1.threePointArc((0.10168, 0.04119), (0.09626, 0.04259))
loop_1 = loop_1.threePointArc((0.08591, 0.04364), (0.07613, 0.04411))
loop_1 = loop_1.threePointArc((0.06009, 0.0446), (0.04487, 0.04469))
loop_1 = loop_1.lineTo(-0.07845, 0.04565)
loop_1 = loop_1.lineTo(-0.09137, 0.04464)
loop_1 = loop_1.lineTo(-0.10156, 0.04249)
loop_1 = loop_1.threePointArc((-0.10682, 0.04066), (-0.1116, 0.03872))
loop_1 = loop_1.lineTo(-0.12192, 0.03129)
loop_1 = loop_1.threePointArc((-0.12533, 0.02426), (-0.12703, 0.02011))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.92)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_021/PART_021.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_021/PART_021_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
