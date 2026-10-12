import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.29612, -0.05998, -0.03504), normal=(0.999, 0.04047, -0.01908), xDir=(0.04048, -0.99918, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07717, 0.93267)
loop_1 = loop_1.threePointArc((-0.00883, 0.93158), (0.06218, 0.92641))
loop_1 = loop_1.threePointArc((0.19756, 0.9021), (0.32687, 0.85903))
loop_1 = loop_1.threePointArc((0.39662, 0.82458), (0.46028, 0.78555))
loop_1 = loop_1.threePointArc((0.5222, 0.74377), (0.57953, 0.69946))
loop_1 = loop_1.threePointArc((0.63806, 0.6484), (0.68927, 0.59265))
loop_1 = loop_1.threePointArc((0.74713, 0.52367), (0.79338, 0.44293))
loop_1 = loop_1.threePointArc((0.83934, 0.3539), (0.87706, 0.25776))
loop_1 = loop_1.threePointArc((0.91281, 0.10914), (0.92429, -0.04312))
loop_1 = loop_1.threePointArc((0.90708, -0.18599), (0.87451, -0.32721))
loop_1 = loop_1.threePointArc((0.86457, -0.36179), (0.85166, -0.39215))
loop_1 = loop_1.lineTo(0.83435, -0.43007)
loop_1 = loop_1.threePointArc((0.8219, -0.45121), (0.80934, -0.46974))
loop_1 = loop_1.lineTo(0.7919, -0.50003)
loop_1 = loop_1.threePointArc((0.75316, -0.58048), (0.70895, -0.65526))
loop_1 = loop_1.threePointArc((0.67754, -0.69244), (0.64519, -0.72486))
loop_1 = loop_1.threePointArc((0.56405, -0.80484), (0.47423, -0.87266))
loop_1 = loop_1.lineTo(0.42469, -0.90224)
loop_1 = loop_1.threePointArc((0.37099, -0.92713), (0.3144, -0.94625))
loop_1 = loop_1.threePointArc((0.18944, -0.98279), (0.06382, -1.00788))
loop_1 = loop_1.threePointArc((-0.05845, -1.01635), (-0.17896, -1.01163))
loop_1 = loop_1.threePointArc((-0.29132, -0.98528), (-0.39998, -0.95003))
loop_1 = loop_1.threePointArc((-0.50087, -0.90901), (-0.59238, -0.85513))
loop_1 = loop_1.threePointArc((-0.69769, -0.76758), (-0.79092, -0.66166))
loop_1 = loop_1.threePointArc((-0.86829, -0.55904), (-0.93261, -0.44672))
loop_1 = loop_1.lineTo(-0.96224, -0.37774)
loop_1 = loop_1.threePointArc((-0.99927, -0.26073), (-1.01801, -0.14148))
loop_1 = loop_1.lineTo(-1.02534, -0.00365)
loop_1 = loop_1.lineTo(-1.02128, 0.0802)
loop_1 = loop_1.threePointArc((-0.98461, 0.24213), (-0.92602, 0.39875))
loop_1 = loop_1.threePointArc((-0.88726, 0.46629), (-0.83874, 0.53051))
loop_1 = loop_1.threePointArc((-0.77847, 0.61356), (-0.7059, 0.6854))
loop_1 = loop_1.threePointArc((-0.60569, 0.76754), (-0.4949, 0.8323))
loop_1 = loop_1.threePointArc((-0.38422, 0.87924), (-0.26869, 0.90864))
loop_1 = loop_1.threePointArc((-0.19722, 0.92488), (-0.12558, 0.93127))
loop_1 = loop_1.threePointArc((-0.10279, 0.93301), (-0.08338, 0.9332))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.6)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fire_truck_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fire_truck_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
