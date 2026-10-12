import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.99, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.22738, 0.06149)
loop_1 = loop_1.threePointArc((-0.21564, 0.05668), (-0.21336, 0.05485))
loop_1 = loop_1.threePointArc((-0.21175, 0.01619), (-0.21168, -0.01694))
loop_1 = loop_1.lineTo(-0.20297, -0.03166)
loop_1 = loop_1.threePointArc((-0.18587, -0.03393), (-0.16975, -0.0352))
loop_1 = loop_1.threePointArc((-0.15414, -0.0354), (-0.13957, -0.03453))
loop_1 = loop_1.threePointArc((-0.01906, -0.02982), (0.10608, -0.03332))
loop_1 = loop_1.threePointArc((0.15762, -0.03515), (0.20673, -0.03483))
loop_1 = loop_1.threePointArc((0.22554, -0.03301), (0.24301, -0.03025))
loop_1 = loop_1.lineTo(0.26275, -0.02902)
loop_1 = loop_1.lineTo(0.26446, -0.04047)
loop_1 = loop_1.threePointArc((0.25533, -0.05335), (0.24858, -0.05535))
loop_1 = loop_1.threePointArc((0.23333, -0.05879), (0.21758, -0.06046))
loop_1 = loop_1.threePointArc((0.17575, -0.06148), (0.13262, -0.06006))
loop_1 = loop_1.threePointArc((0.03726, -0.05706), (-0.05395, -0.05655))
loop_1 = loop_1.threePointArc((-0.10841, -0.0591), (-0.16023, -0.06247))
loop_1 = loop_1.threePointArc((-0.17426, -0.06148), (-0.18826, -0.05938))
loop_1 = loop_1.threePointArc((-0.20141, -0.05723), (-0.21443, -0.0539))
loop_1 = loop_1.threePointArc((-0.23737, -0.0538), (-0.25381, -0.05411))
loop_1 = loop_1.threePointArc((-0.26205, -0.05056), (-0.26464, -0.04801))
loop_1 = loop_1.lineTo(-0.2584, -0.03433)
loop_1 = loop_1.lineTo(-0.24283, -0.03335)
loop_1 = loop_1.lineTo(-0.23662, -0.02333)
loop_1 = loop_1.threePointArc((-0.23622, 0.01009), (-0.23653, 0.04217))
loop_1 = loop_1.threePointArc((-0.2361, 0.04907), (-0.2346, 0.05566))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/recordplayer_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_012/PART_012.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/recordplayer_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_012/PART_012_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
