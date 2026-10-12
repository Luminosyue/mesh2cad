import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.31), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.5578, 0.01683)
loop_1 = loop_1.threePointArc((-0.55497, -0.03566), (-0.54853, -0.0857))
loop_1 = loop_1.threePointArc((-0.54322, -0.12286), (-0.53431, -0.15662))
loop_1 = loop_1.threePointArc((-0.49929, -0.24099), (-0.45675, -0.31637))
loop_1 = loop_1.threePointArc((-0.40012, -0.38036), (-0.34154, -0.43601))
loop_1 = loop_1.threePointArc((-0.29921, -0.46429), (-0.25741, -0.48731))
loop_1 = loop_1.threePointArc((-0.22072, -0.50802), (-0.18436, -0.5229))
loop_1 = loop_1.threePointArc((-0.09765, -0.54161), (-0.0143, -0.55183))
loop_1 = loop_1.threePointArc((0.026, -0.5497), (0.06343, -0.54629))
loop_1 = loop_1.threePointArc((0.12301, -0.53914), (0.17699, -0.52245))
loop_1 = loop_1.threePointArc((0.24174, -0.49814), (0.29984, -0.46844))
loop_1 = loop_1.lineTo(0.36037, -0.42569)
loop_1 = loop_1.threePointArc((0.41188, -0.38075), (0.45241, -0.33053))
loop_1 = loop_1.threePointArc((0.47613, -0.29582), (0.49571, -0.2617))
loop_1 = loop_1.threePointArc((0.51778, -0.21877), (0.53122, -0.17558))
loop_1 = loop_1.threePointArc((0.54799, -0.10184), (0.55818, -0.03107))
loop_1 = loop_1.threePointArc((0.55811, -0.00599), (0.5551, 0.01674))
loop_1 = loop_1.lineTo(0.54798, 0.10297)
loop_1 = loop_1.threePointArc((0.51821, 0.20719), (0.47001, 0.29816))
loop_1 = loop_1.threePointArc((0.43205, 0.34552), (0.39143, 0.38566))
loop_1 = loop_1.threePointArc((0.35826, 0.41773), (0.32522, 0.4509))
loop_1 = loop_1.threePointArc((0.30614, 0.46527), (0.28795, 0.4772))
loop_1 = loop_1.threePointArc((0.2178, 0.5092), (0.14895, 0.53304))
loop_1 = loop_1.threePointArc((0.10815, 0.54074), (0.06957, 0.54384))
loop_1 = loop_1.threePointArc((0.01557, 0.54859), (-0.03533, 0.54947))
loop_1 = loop_1.threePointArc((-0.09453, 0.53961), (-0.14985, 0.52843))
loop_1 = loop_1.threePointArc((-0.22305, 0.50023), (-0.2878, 0.46407))
loop_1 = loop_1.threePointArc((-0.32876, 0.43284), (-0.36543, 0.40141))
loop_1 = loop_1.lineTo(-0.41496, 0.36109)
loop_1 = loop_1.threePointArc((-0.43554, 0.3392), (-0.45108, 0.31627))
loop_1 = loop_1.threePointArc((-0.48336, 0.2688), (-0.51194, 0.22304))
loop_1 = loop_1.threePointArc((-0.53463, 0.16486), (-0.54901, 0.10763))
loop_1 = loop_1.lineTo(-0.55774, 0.01798)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.65)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/construction_30_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_026/PART_026.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/construction_30_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_026/PART_026_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
