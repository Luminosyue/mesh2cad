import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.19759, -0.28527, 0.87407), normal=(-0.22159, 0.29961, -0.92797), xDir=(0.0, -0.95163, -0.30725))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.2596, -0.22133)
loop_1 = loop_1.threePointArc((0.25414, -0.22661), (0.24779, -0.23134))
loop_1 = loop_1.lineTo(0.23272, -0.23542)
loop_1 = loop_1.lineTo(0.2218, -0.23369)
loop_1 = loop_1.lineTo(0.20785, -0.22955)
loop_1 = loop_1.lineTo(0.13445, -0.19994)
loop_1 = loop_1.lineTo(0.09607, -0.18362)
loop_1 = loop_1.lineTo(0.05313, -0.16398)
loop_1 = loop_1.lineTo(0.0228, -0.15081)
loop_1 = loop_1.threePointArc((-0.02445, -0.12945), (-0.07257, -0.10681))
loop_1 = loop_1.threePointArc((-0.08564, -0.10132), (-0.09575, -0.09597))
loop_1 = loop_1.threePointArc((-0.11087, -0.08975), (-0.12265, -0.08402))
loop_1 = loop_1.lineTo(-0.14258, -0.07538)
loop_1 = loop_1.threePointArc((-0.17625, -0.06091), (-0.20956, -0.04588))
loop_1 = loop_1.threePointArc((-0.23184, -0.0367), (-0.24986, -0.02836))
loop_1 = loop_1.threePointArc((-0.26699, -0.02118), (-0.28115, -0.01591))
loop_1 = loop_1.threePointArc((-0.29661, -0.0092), (-0.30925, -0.00351))
loop_1 = loop_1.lineTo(-0.33877, 0.02934)
loop_1 = loop_1.lineTo(-0.3359, 0.04561)
loop_1 = loop_1.threePointArc((-0.32573, 0.06915), (-0.31523, 0.09008))
loop_1 = loop_1.lineTo(-0.27051, 0.18824)
loop_1 = loop_1.threePointArc((-0.26345, 0.20086), (-0.2566, 0.21022))
loop_1 = loop_1.lineTo(-0.24517, 0.22075)
loop_1 = loop_1.threePointArc((-0.23677, 0.22282), (-0.22801, 0.22496))
loop_1 = loop_1.threePointArc((-0.21874, 0.2238), (-0.21281, 0.22261))
loop_1 = loop_1.threePointArc((-0.19182, 0.21656), (-0.17331, 0.21003))
loop_1 = loop_1.threePointArc((-0.13357, 0.19486), (-0.09617, 0.17904))
loop_1 = loop_1.threePointArc((-0.06921, 0.1679), (-0.04747, 0.15973))
loop_1 = loop_1.lineTo(-0.01373, 0.14567)
loop_1 = loop_1.lineTo(0.00858, 0.13557)
loop_1 = loop_1.threePointArc((0.02423, 0.12977), (0.03692, 0.12391))
loop_1 = loop_1.lineTo(0.09863, 0.09577)
loop_1 = loop_1.threePointArc((0.13645, 0.07846), (0.17039, 0.0638))
loop_1 = loop_1.lineTo(0.19964, 0.05061)
loop_1 = loop_1.lineTo(0.27438, 0.01757)
loop_1 = loop_1.lineTo(0.30039, 0.00555)
loop_1 = loop_1.threePointArc((0.31104, 0.00015), (0.31884, -0.00429))
loop_1 = loop_1.threePointArc((0.32979, -0.01515), (0.33646, -0.02674))
loop_1 = loop_1.lineTo(0.33724, -0.04388)
loop_1 = loop_1.threePointArc((0.33231, -0.06083), (0.32601, -0.07518))
loop_1 = loop_1.lineTo(0.3116, -0.10765)
loop_1 = loop_1.lineTo(0.29216, -0.1537)
loop_1 = loop_1.lineTo(0.26935, -0.20536)
loop_1 = loop_1.lineTo(0.25973, -0.22114)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.88)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/construction_30_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_014/PART_014.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/construction_30_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_014/PART_014_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
