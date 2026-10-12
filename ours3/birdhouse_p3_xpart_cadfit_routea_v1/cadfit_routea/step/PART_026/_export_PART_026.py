import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.12628, 0.13867)
loop_1 = loop_1.threePointArc((-0.11861, 0.13724), (-0.11068, 0.1355))
loop_1 = loop_1.threePointArc((-0.08393, 0.10356), (-0.06473, 0.08111))
loop_1 = loop_1.threePointArc((-0.05204, 0.06478), (-0.03949, 0.04973))
loop_1 = loop_1.threePointArc((-0.01073, 0.01329), (0.01733, -0.021))
loop_1 = loop_1.lineTo(0.05135, -0.06314)
loop_1 = loop_1.threePointArc((0.0671, -0.0826), (0.08284, -0.10305))
loop_1 = loop_1.lineTo(0.09797, -0.11773)
loop_1 = loop_1.threePointArc((0.11147, -0.11566), (0.11741, -0.10985))
loop_1 = loop_1.lineTo(0.12937, -0.11741)
loop_1 = loop_1.lineTo(0.11955, -0.13309)
loop_1 = loop_1.lineTo(0.10433, -0.1438)
loop_1 = loop_1.lineTo(0.08879, -0.14074)
loop_1 = loop_1.lineTo(0.07837, -0.13162)
loop_1 = loop_1.lineTo(0.03906, -0.08514)
loop_1 = loop_1.threePointArc((0.0229, -0.06489), (0.00723, -0.04591))
loop_1 = loop_1.threePointArc((-0.02834, -0.00174), (-0.06491, 0.04429))
loop_1 = loop_1.lineTo(-0.09032, 0.07466)
loop_1 = loop_1.threePointArc((-0.10082, 0.08791), (-0.11129, 0.10172))
loop_1 = loop_1.lineTo(-0.12722, 0.11842)
loop_1 = loop_1.lineTo(-0.1349, 0.12927)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/birdhouse_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_026/PART_026.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/birdhouse_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_026/PART_026_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
