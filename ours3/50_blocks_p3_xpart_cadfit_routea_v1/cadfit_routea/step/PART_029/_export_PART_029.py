import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.97), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.41272, -0.0078)
loop_1 = loop_1.threePointArc((-0.41162, -0.02109), (-0.40973, -0.03374))
loop_1 = loop_1.threePointArc((-0.39396, -0.086), (-0.37061, -0.13208))
loop_1 = loop_1.threePointArc((-0.34842, -0.16017), (-0.32405, -0.18334))
loop_1 = loop_1.threePointArc((-0.26286, -0.22058), (-0.19743, -0.23911))
loop_1 = loop_1.threePointArc((-0.16127, -0.24164), (-0.12728, -0.24012))
loop_1 = loop_1.threePointArc((-0.09116, -0.23364), (-0.05809, -0.22381))
loop_1 = loop_1.threePointArc((-0.0174, -0.20482), (0.01565, -0.17829))
loop_1 = loop_1.threePointArc((0.04219, -0.15125), (0.06494, -0.12388))
loop_1 = loop_1.threePointArc((0.08237, -0.12285), (0.09339, -0.1284))
loop_1 = loop_1.threePointArc((0.13488, -0.16254), (0.17605, -0.19226))
loop_1 = loop_1.threePointArc((0.20204, -0.20771), (0.2276, -0.2198))
loop_1 = loop_1.threePointArc((0.24298, -0.22442), (0.25746, -0.22664))
loop_1 = loop_1.threePointArc((0.2648, -0.22758), (0.27111, -0.22672))
loop_1 = loop_1.lineTo(0.28479, -0.22525)
loop_1 = loop_1.threePointArc((0.2973, -0.21964), (0.30776, -0.21298))
loop_1 = loop_1.threePointArc((0.32331, -0.19652), (0.33483, -0.17903))
loop_1 = loop_1.threePointArc((0.34845, -0.15129), (0.35935, -0.1245))
loop_1 = loop_1.threePointArc((0.38736, -0.04784), (0.41012, 0.02636))
loop_1 = loop_1.threePointArc((0.4134, 0.04382), (0.41554, 0.05996))
loop_1 = loop_1.lineTo(0.41537, 0.07981)
loop_1 = loop_1.threePointArc((0.41072, 0.10119), (0.40336, 0.12007))
loop_1 = loop_1.lineTo(0.39028, 0.14543)
loop_1 = loop_1.threePointArc((0.38237, 0.15658), (0.3747, 0.16627))
loop_1 = loop_1.threePointArc((0.35198, 0.18766), (0.32831, 0.20481))
loop_1 = loop_1.threePointArc((0.29041, 0.22473), (0.25217, 0.23776))
loop_1 = loop_1.threePointArc((0.19915, 0.24584), (0.14847, 0.24376))
loop_1 = loop_1.threePointArc((0.13185, 0.2398), (0.11713, 0.23452))
loop_1 = loop_1.threePointArc((0.07926, 0.21582), (0.04634, 0.19338))
loop_1 = loop_1.lineTo(0.0281, 0.18267)
loop_1 = loop_1.threePointArc((0.01651, 0.18628), (0.00544, 0.19056))
loop_1 = loop_1.threePointArc((-0.02789, 0.21471), (-0.06167, 0.23364))
loop_1 = loop_1.lineTo(-0.08159, 0.24061)
loop_1 = loop_1.threePointArc((-0.14778, 0.24797), (-0.2103, 0.23862))
loop_1 = loop_1.threePointArc((-0.29619, 0.19998), (-0.36326, 0.14039))
loop_1 = loop_1.lineTo(-0.37824, 0.11584)
loop_1 = loop_1.threePointArc((-0.3919, 0.08643), (-0.40189, 0.05773))
loop_1 = loop_1.lineTo(-0.40933, 0.0295)
loop_1 = loop_1.threePointArc((-0.41204, 0.01056), (-0.41264, -0.00705))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.95)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/50_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_029/PART_029.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/50_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_029/PART_029_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
