import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.99), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.20471, 0.05266)
loop_1 = loop_1.lineTo(-0.19425, 0.01775)
loop_1 = loop_1.lineTo(-0.15572, 0.01466)
loop_1 = loop_1.threePointArc((-0.1753, 0.01114), (-0.19465, 0.01014))
loop_1 = loop_1.lineTo(-0.20307, -0.02514)
loop_1 = loop_1.lineTo(-0.20313, -0.06258)
loop_1 = loop_1.lineTo(-0.19427, -0.07477)
loop_1 = loop_1.lineTo(-0.15515, -0.08681)
loop_1 = loop_1.lineTo(-0.00234, -0.08592)
loop_1 = loop_1.threePointArc((0.05473, -0.0858), (0.11376, -0.08641))
loop_1 = loop_1.threePointArc((0.15218, -0.08629), (0.18868, -0.08597))
loop_1 = loop_1.lineTo(0.21451, -0.06185)
loop_1 = loop_1.lineTo(0.21647, -0.02235)
loop_1 = loop_1.threePointArc((0.2134, -0.00321), (0.21016, 0.01472))
loop_1 = loop_1.threePointArc((0.21329, 0.03355), (0.21664, 0.05264))
loop_1 = loop_1.lineTo(0.18798, 0.08745)
loop_1 = loop_1.threePointArc((0.04486, 0.08873), (-0.09216, 0.08947))
loop_1 = loop_1.lineTo(-0.15712, 0.08866)
loop_1 = loop_1.threePointArc((-0.17665, 0.0823), (-0.19487, 0.07587))
loop_1 = loop_1.threePointArc((-0.19992, 0.06398), (-0.20456, 0.05302))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_038/PART_038.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_038/PART_038_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
