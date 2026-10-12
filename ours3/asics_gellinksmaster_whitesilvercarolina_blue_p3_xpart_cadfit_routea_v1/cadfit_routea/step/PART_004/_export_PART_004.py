import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.6857, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.21721, 0.13387)
loop_1 = loop_1.lineTo(0.30604, 0.11239)
loop_1 = loop_1.threePointArc((0.31533, 0.10463), (0.32338, 0.09659))
loop_1 = loop_1.lineTo(0.3699, 0.01006)
loop_1 = loop_1.threePointArc((0.38816, -0.03476), (0.406, -0.07658))
loop_1 = loop_1.lineTo(0.48299, -0.15356)
loop_1 = loop_1.lineTo(0.51439, -0.16626)
loop_1 = loop_1.threePointArc((0.551, -0.19073), (0.58597, -0.21241))
loop_1 = loop_1.lineTo(0.65526, -0.25264)
loop_1 = loop_1.lineTo(0.56784, -0.27598)
loop_1 = loop_1.lineTo(0.4776, -0.28576)
loop_1 = loop_1.threePointArc((0.23454, -0.27971), (0.00225, -0.2772))
loop_1 = loop_1.lineTo(-0.26678, -0.27007)
loop_1 = loop_1.threePointArc((-0.48698, -0.26646), (-0.71508, -0.2603))
loop_1 = loop_1.threePointArc((-0.77843, -0.26023), (-0.83812, -0.26135))
loop_1 = loop_1.lineTo(-0.8559, -0.25118)
loop_1 = loop_1.lineTo(-0.88017, -0.16533)
loop_1 = loop_1.lineTo(-0.83868, -0.10416)
loop_1 = loop_1.threePointArc((-0.79592, -0.07343), (-0.75083, -0.04415))
loop_1 = loop_1.lineTo(-0.66705, -0.03567)
loop_1 = loop_1.lineTo(-0.57223, 0.00262)
loop_1 = loop_1.threePointArc((-0.56099, 0.01715), (-0.55277, 0.03147))
loop_1 = loop_1.lineTo(-0.50973, 0.09875)
loop_1 = loop_1.lineTo(-0.48432, 0.11928)
loop_1 = loop_1.lineTo(-0.39205, 0.13184)
loop_1 = loop_1.lineTo(-0.29969, 0.11934)
loop_1 = loop_1.lineTo(-0.21755, 0.09637)
loop_1 = loop_1.lineTo(-0.13166, 0.05339)
loop_1 = loop_1.lineTo(-0.00997, 0.08905)
loop_1 = loop_1.threePointArc((0.04025, 0.10435), (0.09239, 0.11623))
loop_1 = loop_1.lineTo(0.13252, 0.12508)
loop_1 = loop_1.lineTo(0.21607, 0.13375)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.29)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asics_gellinksmaster_whitesilvercarolina_blue_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_004/PART_004.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asics_gellinksmaster_whitesilvercarolina_blue_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_004/PART_004_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
