import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.99, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0522, 0.87403)
loop_1 = loop_1.threePointArc((0.00623, 0.87202), (0.06236, 0.87217))
loop_1 = loop_1.threePointArc((0.07148, 0.86318), (0.07394, 0.85741))
loop_1 = loop_1.threePointArc((0.06572, 0.8473), (0.05903, 0.84335))
loop_1 = loop_1.threePointArc((0.02377, 0.84302), (-0.01152, 0.84469))
loop_1 = loop_1.lineTo(-0.03327, 0.84494)
loop_1 = loop_1.lineTo(-0.06106, 0.56771)
loop_1 = loop_1.threePointArc((-0.07073, 0.41952), (-0.07365, 0.27827))
loop_1 = loop_1.threePointArc((-0.07615, 0.11972), (-0.07633, -0.03126))
loop_1 = loop_1.threePointArc((-0.06834, -0.20242), (-0.05841, -0.36533))
loop_1 = loop_1.threePointArc((-0.03324, -0.52646), (-0.00032, -0.6782))
loop_1 = loop_1.threePointArc((0.01286, -0.74324), (0.02735, -0.80391))
loop_1 = loop_1.lineTo(0.05699, -0.81687)
loop_1 = loop_1.threePointArc((0.06268, -0.82945), (0.06428, -0.84253))
loop_1 = loop_1.lineTo(0.06916, -0.85406)
loop_1 = loop_1.lineTo(0.10658, -0.85442)
loop_1 = loop_1.lineTo(0.11098, -0.87886)
loop_1 = loop_1.threePointArc((0.08937, -0.88094), (0.06681, -0.87933))
loop_1 = loop_1.lineTo(0.04715, -0.8781)
loop_1 = loop_1.threePointArc((0.03961, -0.87058), (0.03791, -0.86113))
loop_1 = loop_1.threePointArc((0.03591, -0.85124), (0.03425, -0.84302))
loop_1 = loop_1.threePointArc((0.02303, -0.83955), (0.01274, -0.83857))
loop_1 = loop_1.threePointArc((0.00478, -0.82868), (0.0034, -0.82218))
loop_1 = loop_1.threePointArc((-0.02995, -0.67616), (-0.06151, -0.5249))
loop_1 = loop_1.lineTo(-0.08423, -0.40495)
loop_1 = loop_1.lineTo(-0.09692, -0.2237)
loop_1 = loop_1.lineTo(-0.10945, -0.05329)
loop_1 = loop_1.lineTo(-0.10547, -0.02553)
loop_1 = loop_1.threePointArc((-0.10611, -0.01909), (-0.10496, -0.01387))
loop_1 = loop_1.lineTo(-0.1023, 0.03814)
loop_1 = loop_1.threePointArc((-0.10217, 0.06071), (-0.1034, 0.08107))
loop_1 = loop_1.lineTo(-0.10159, 0.09287)
loop_1 = loop_1.threePointArc((-0.10972, 0.11715), (-0.11012, 0.14246))
loop_1 = loop_1.lineTo(-0.10258, 0.31583)
loop_1 = loop_1.threePointArc((-0.09326, 0.51898), (-0.07201, 0.72853))
loop_1 = loop_1.threePointArc((-0.0655, 0.79861), (-0.06063, 0.86476))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.98)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/recordplayer_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/recordplayer_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
