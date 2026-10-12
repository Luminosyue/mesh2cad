import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.83), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39604, -0.00109)
loop_1 = loop_1.lineTo(-0.39091, -0.06244)
loop_1 = loop_1.threePointArc((-0.38325, -0.10481), (-0.3728, -0.14393))
loop_1 = loop_1.threePointArc((-0.35772, -0.18139), (-0.34024, -0.21505))
loop_1 = loop_1.threePointArc((-0.29585, -0.27175), (-0.24477, -0.31704))
loop_1 = loop_1.threePointArc((-0.20024, -0.3494), (-0.1548, -0.37477))
loop_1 = loop_1.threePointArc((-0.11377, -0.39144), (-0.07413, -0.40432))
loop_1 = loop_1.threePointArc((0.0052, -0.41282), (0.08076, -0.40734))
loop_1 = loop_1.threePointArc((0.12016, -0.3981), (0.15664, -0.38741))
loop_1 = loop_1.threePointArc((0.19964, -0.36768), (0.23869, -0.34623))
loop_1 = loop_1.threePointArc((0.25595, -0.33419), (0.27071, -0.32164))
loop_1 = loop_1.threePointArc((0.3063, -0.29024), (0.33717, -0.25787))
loop_1 = loop_1.threePointArc((0.36016, -0.22232), (0.37979, -0.18775))
loop_1 = loop_1.lineTo(0.39831, -0.15345)
loop_1 = loop_1.threePointArc((0.40913, -0.11966), (0.41649, -0.08724))
loop_1 = loop_1.threePointArc((0.42423, -0.04051), (0.42633, 0.0041))
loop_1 = loop_1.threePointArc((0.4198, 0.06336), (0.4059, 0.11801))
loop_1 = loop_1.threePointArc((0.38988, 0.16449), (0.36789, 0.20531))
loop_1 = loop_1.threePointArc((0.34826, 0.23685), (0.32743, 0.26463))
loop_1 = loop_1.threePointArc((0.30409, 0.28769), (0.28067, 0.30743))
loop_1 = loop_1.threePointArc((0.23641, 0.33918), (0.19086, 0.36315))
loop_1 = loop_1.threePointArc((0.11853, 0.38801), (0.04722, 0.4016))
loop_1 = loop_1.threePointArc((0.03012, 0.4037), (0.01443, 0.40445))
loop_1 = loop_1.threePointArc((-0.02659, 0.40264), (-0.06491, 0.39819))
loop_1 = loop_1.threePointArc((-0.12756, 0.37935), (-0.18343, 0.35264))
loop_1 = loop_1.threePointArc((-0.21407, 0.33339), (-0.24076, 0.3124))
loop_1 = loop_1.threePointArc((-0.26094, 0.29619), (-0.27856, 0.27983))
loop_1 = loop_1.threePointArc((-0.31386, 0.23857), (-0.34444, 0.19738))
loop_1 = loop_1.threePointArc((-0.37351, 0.1309), (-0.39066, 0.06416))
loop_1 = loop_1.threePointArc((-0.39461, 0.03099), (-0.39585, -0.00024))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.58)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/android_lego_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/android_lego_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
