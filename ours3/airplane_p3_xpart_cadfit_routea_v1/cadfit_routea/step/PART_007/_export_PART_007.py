import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.72, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.69858, 0.20431)
loop_1 = loop_1.threePointArc((-0.72363, 0.20251), (-0.74715, 0.19718))
loop_1 = loop_1.threePointArc((-0.76296, 0.18962), (-0.77517, 0.17939))
loop_1 = loop_1.threePointArc((-0.7817, 0.17382), (-0.78443, 0.16711))
loop_1 = loop_1.lineTo(-0.79061, 0.15183)
loop_1 = loop_1.threePointArc((-0.79375, 0.12972), (-0.79524, 0.10927))
loop_1 = loop_1.lineTo(-0.79066, 0.08927)
loop_1 = loop_1.lineTo(-0.78082, 0.06953)
loop_1 = loop_1.lineTo(-0.75962, 0.04823)
loop_1 = loop_1.threePointArc((-0.73958, 0.03657), (-0.7196, 0.02914))
loop_1 = loop_1.threePointArc((-0.61913, 0.00215), (-0.52245, -0.02206))
loop_1 = loop_1.threePointArc((-0.48025, -0.02937), (-0.4403, -0.03391))
loop_1 = loop_1.lineTo(-0.23036, -0.06227)
loop_1 = loop_1.lineTo(0.00803, -0.09512)
loop_1 = loop_1.threePointArc((0.0336, -0.09822), (0.05913, -0.10241))
loop_1 = loop_1.threePointArc((0.21887, -0.12352), (0.37155, -0.1415))
loop_1 = loop_1.threePointArc((0.39277, -0.14158), (0.41212, -0.14014))
loop_1 = loop_1.threePointArc((0.45017, -0.12597), (0.48139, -0.10414))
loop_1 = loop_1.threePointArc((0.49317, -0.09475), (0.50186, -0.08437))
loop_1 = loop_1.threePointArc((0.51048, -0.07421), (0.5149, -0.06324))
loop_1 = loop_1.lineTo(0.51472, -0.03356)
loop_1 = loop_1.threePointArc((0.48652, -0.00656), (0.45746, 0.01574))
loop_1 = loop_1.threePointArc((0.42865, 0.03025), (0.39944, 0.03742))
loop_1 = loop_1.threePointArc((0.33417, 0.04809), (0.27191, 0.05464))
loop_1 = loop_1.threePointArc((0.1269, 0.07253), (-0.02292, 0.09266))
loop_1 = loop_1.threePointArc((-0.14048, 0.10539), (-0.26168, 0.12081))
loop_1 = loop_1.lineTo(-0.47879, 0.14863)
loop_1 = loop_1.threePointArc((-0.50837, 0.15544), (-0.53771, 0.16432))
loop_1 = loop_1.lineTo(-0.66044, 0.19777)
loop_1 = loop_1.threePointArc((-0.67972, 0.20202), (-0.69763, 0.20425))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.58)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if str(k).startswith('solid_')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_007/PART_007.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_007/PART_007_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
