import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.8, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.73469, 0.65181)
loop_1 = loop_1.lineTo(0.80481, 0.64959)
loop_1 = loop_1.lineTo(0.83193, 0.63317)
loop_1 = loop_1.threePointArc((0.83851, 0.61767), (0.84208, 0.60227))
loop_1 = loop_1.threePointArc((0.84077, 0.55385), (0.83696, 0.50541))
loop_1 = loop_1.threePointArc((0.83516, 0.46498), (0.83145, 0.42484))
loop_1 = loop_1.threePointArc((0.81007, 0.31455), (0.77984, 0.20339))
loop_1 = loop_1.threePointArc((0.7302, 0.07924), (0.66644, -0.04255))
loop_1 = loop_1.threePointArc((0.60399, -0.13983), (0.53046, -0.2319))
loop_1 = loop_1.threePointArc((0.46806, -0.29971), (0.39855, -0.36338))
loop_1 = loop_1.threePointArc((0.33471, -0.41466), (0.26666, -0.46255))
loop_1 = loop_1.threePointArc((0.19089, -0.50353), (0.11206, -0.54223))
loop_1 = loop_1.lineTo(-0.01991, -0.59408)
loop_1 = loop_1.threePointArc((-0.09358, -0.61509), (-0.1694, -0.63334))
loop_1 = loop_1.threePointArc((-0.27048, -0.64762), (-0.37489, -0.6492))
loop_1 = loop_1.threePointArc((-0.46106, -0.65069), (-0.54898, -0.64948))
loop_1 = loop_1.threePointArc((-0.58551, -0.64578), (-0.62133, -0.63941))
loop_1 = loop_1.threePointArc((-0.65414, -0.63073), (-0.68585, -0.61982))
loop_1 = loop_1.threePointArc((-0.72929, -0.59266), (-0.76889, -0.55973))
loop_1 = loop_1.threePointArc((-0.81502, -0.4834), (-0.83702, -0.39507))
loop_1 = loop_1.threePointArc((-0.84164, -0.33079), (-0.84183, -0.26552))
loop_1 = loop_1.threePointArc((-0.84284, -0.12771), (-0.84498, 0.00295))
loop_1 = loop_1.threePointArc((-0.84003, 0.13256), (-0.83201, 0.26559))
loop_1 = loop_1.threePointArc((-0.83086, 0.37606), (-0.83519, 0.48039))
loop_1 = loop_1.threePointArc((-0.83908, 0.53119), (-0.84011, 0.58248))
loop_1 = loop_1.lineTo(-0.83347, 0.6075)
loop_1 = loop_1.lineTo(-0.81841, 0.62984)
loop_1 = loop_1.threePointArc((-0.80313, 0.63826), (-0.78772, 0.64294))
loop_1 = loop_1.threePointArc((-0.6009, 0.64361), (-0.4081, 0.64184))
loop_1 = loop_1.threePointArc((-0.04242, 0.64247), (0.30687, 0.64755))
loop_1 = loop_1.lineTo(0.73312, 0.65178)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.58)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/mini_fire_engine_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/mini_fire_engine_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
