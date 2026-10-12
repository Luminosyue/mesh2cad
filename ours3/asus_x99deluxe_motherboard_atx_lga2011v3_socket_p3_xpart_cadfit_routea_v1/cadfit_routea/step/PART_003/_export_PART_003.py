import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.27, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01208, 0.99774)
loop_1 = loop_1.threePointArc((0.02303, 0.99381), (0.03029, 0.98414))
loop_1 = loop_1.threePointArc((0.03944, 0.89656), (0.03973, 0.81136))
loop_1 = loop_1.threePointArc((0.03816, 0.57089), (0.03395, 0.32182))
loop_1 = loop_1.threePointArc((0.03362, 0.03409), (0.02719, -0.26415))
loop_1 = loop_1.threePointArc((0.01592, -0.6321), (0.00936, -0.9841))
loop_1 = loop_1.threePointArc((-0.00833, -0.99435), (-0.01779, -0.99473))
loop_1 = loop_1.threePointArc((-0.02619, -0.99714), (-0.03379, -0.99753))
loop_1 = loop_1.threePointArc((-0.03566, -0.78009), (-0.02634, -0.5615))
loop_1 = loop_1.threePointArc((-0.01886, -0.31558), (-0.01395, -0.08078))
loop_1 = loop_1.threePointArc((-0.008, 0.13346), (-0.00561, 0.33787))
loop_1 = loop_1.threePointArc((-0.00063, 0.59611), (-0.00205, 0.84283))
loop_1 = loop_1.lineTo(-0.00124, 0.98572)
loop_1 = loop_1.lineTo(0.01208, 0.99774)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.57)

result = solid_1

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asus_x99deluxe_motherboard_atx_lga2011v3_socket_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asus_x99deluxe_motherboard_atx_lga2011v3_socket_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
