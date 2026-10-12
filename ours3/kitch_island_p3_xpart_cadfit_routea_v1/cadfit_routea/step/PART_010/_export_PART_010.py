import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00314, 0.07714, 0.08362), normal=(-0.06038, -0.99815, -0.00747), xDir=(-0.99818, 0.06038, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01453, 1.08286)
loop_1 = loop_1.lineTo(-0.00488, 1.0813)
loop_1 = loop_1.lineTo(-0.0115, 1.07036)
loop_1 = loop_1.lineTo(-0.01191, 0.17473)
loop_1 = loop_1.lineTo(-0.01243, 0.14427)
loop_1 = loop_1.lineTo(-0.01642, 0.12149)
loop_1 = loop_1.lineTo(-0.03246, 0.10552)
loop_1 = loop_1.lineTo(-0.04488, 0.08614)
loop_1 = loop_1.lineTo(-0.0404, 0.07051)
loop_1 = loop_1.lineTo(-0.02978, 0.0524)
loop_1 = loop_1.lineTo(-0.02618, 0.02104)
loop_1 = loop_1.lineTo(-0.02717, 0.00859)
loop_1 = loop_1.threePointArc((-0.03022, -0.04918), (-0.02452, -0.10444))
loop_1 = loop_1.threePointArc((-0.02048, -0.16149), (-0.01992, -0.21775))
loop_1 = loop_1.threePointArc((-0.01931, -0.28527), (-0.02476, -0.34896))
loop_1 = loop_1.lineTo(-0.02664, -0.35952)
loop_1 = loop_1.lineTo(-0.0301, -0.37889)
loop_1 = loop_1.lineTo(-0.03384, -0.41764)
loop_1 = loop_1.lineTo(-0.03404, -0.42845)
loop_1 = loop_1.threePointArc((-0.03607, -0.5811), (-0.0337, -0.72764))
loop_1 = loop_1.threePointArc((-0.03414, -0.8208), (-0.03316, -0.90205))
loop_1 = loop_1.lineTo(-0.01697, -0.91472)
loop_1 = loop_1.lineTo(-0.00578, -0.91675)
loop_1 = loop_1.lineTo(0.01363, -0.91406)
loop_1 = loop_1.lineTo(0.02149, -0.90205)
loop_1 = loop_1.threePointArc((0.02534, -0.49672), (0.02311, -0.11592))
loop_1 = loop_1.lineTo(0.02323, -0.04723)
loop_1 = loop_1.lineTo(0.02657, -0.03012)
loop_1 = loop_1.lineTo(0.0529, -0.01752)
loop_1 = loop_1.lineTo(0.05111, 0.12489)
loop_1 = loop_1.threePointArc((0.04818, 0.23833), (0.0401, 0.33799))
loop_1 = loop_1.threePointArc((0.03716, 0.43742), (0.03686, 0.53179))
loop_1 = loop_1.threePointArc((0.03552, 0.61305), (0.03257, 0.68311))
loop_1 = loop_1.threePointArc((0.02641, 0.77212), (0.02609, 0.86118))
loop_1 = loop_1.lineTo(0.02421, 1.06822)
loop_1 = loop_1.lineTo(0.01731, 1.08033)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_010/PART_010.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_010/PART_010_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
