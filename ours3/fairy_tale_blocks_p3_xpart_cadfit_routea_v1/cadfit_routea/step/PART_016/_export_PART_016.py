import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.49, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.87264, 0.52567)
loop_1 = loop_1.threePointArc((-0.73274, 0.52165), (-0.5984, 0.52066))
loop_1 = loop_1.threePointArc((-0.57287, 0.51178), (-0.55021, 0.5013))
loop_1 = loop_1.lineTo(-0.53424, 0.48749)
loop_1 = loop_1.lineTo(-0.51828, 0.46518)
loop_1 = loop_1.threePointArc((-0.5092, 0.43458), (-0.50429, 0.40368))
loop_1 = loop_1.threePointArc((-0.48607, 0.32995), (-0.46036, 0.26412))
loop_1 = loop_1.threePointArc((-0.3604, 0.1334), (-0.23313, 0.04344))
loop_1 = loop_1.threePointArc((-0.18587, 0.02303), (-0.1417, 0.00589))
loop_1 = loop_1.threePointArc((-0.11056, 3e-05), (-0.08245, -0.00411))
loop_1 = loop_1.threePointArc((0.01048, -0.00945), (0.09707, 0.0025))
loop_1 = loop_1.threePointArc((0.13602, 0.00974), (0.17046, 0.02038))
loop_1 = loop_1.threePointArc((0.22842, 0.04862), (0.27912, 0.08028))
loop_1 = loop_1.threePointArc((0.36553, 0.16037), (0.43037, 0.25085))
loop_1 = loop_1.threePointArc((0.4641, 0.32646), (0.48117, 0.40171))
loop_1 = loop_1.lineTo(0.48892, 0.43839)
loop_1 = loop_1.lineTo(0.49501, 0.45558)
loop_1 = loop_1.threePointArc((0.51599, 0.4817), (0.543, 0.49887))
loop_1 = loop_1.threePointArc((0.58981, 0.50849), (0.63739, 0.50902))
loop_1 = loop_1.threePointArc((0.74178, 0.50955), (0.84848, 0.50759))
loop_1 = loop_1.threePointArc((0.88744, 0.50516), (0.9253, 0.49915))
loop_1 = loop_1.threePointArc((0.95393, 0.48296), (0.97469, 0.45844))
loop_1 = loop_1.lineTo(0.98464, 0.43023)
loop_1 = loop_1.threePointArc((0.98641, 0.40518), (0.98527, 0.38129))
loop_1 = loop_1.threePointArc((0.98298, 0.07448), (0.98263, -0.21805))
loop_1 = loop_1.threePointArc((0.98106, -0.3078), (0.97875, -0.39904))
loop_1 = loop_1.threePointArc((0.95195, -0.4616), (0.89256, -0.49585))
loop_1 = loop_1.threePointArc((0.84455, -0.50315), (0.79594, -0.50409))
loop_1 = loop_1.threePointArc((0.43246, -0.50947), (0.05599, -0.51125))
loop_1 = loop_1.lineTo(-0.21082, -0.51003)
loop_1 = loop_1.threePointArc((-0.51437, -0.5072), (-0.82834, -0.50169))
loop_1 = loop_1.threePointArc((-0.87179, -0.49829), (-0.91398, -0.49039))
loop_1 = loop_1.threePointArc((-0.94303, -0.47748), (-0.96665, -0.4578))
loop_1 = loop_1.lineTo(-0.98333, -0.43363)
loop_1 = loop_1.threePointArc((-0.98939, -0.4084), (-0.98974, -0.38358))
loop_1 = loop_1.lineTo(-0.98979, 0.41719)
loop_1 = loop_1.threePointArc((-0.98967, 0.43683), (-0.98787, 0.45498))
loop_1 = loop_1.threePointArc((-0.97515, 0.48688), (-0.95181, 0.51086))
loop_1 = loop_1.threePointArc((-0.92662, 0.52125), (-0.90071, 0.52539))
loop_1 = loop_1.lineTo(-0.87481, 0.52536)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.94)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fairy_tale_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_016/PART_016.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fairy_tale_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_016/PART_016_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
