import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00116, 0.04984)
loop_1 = loop_1.lineTo(-0.02574, 0.03598)
loop_1 = loop_1.lineTo(-0.04039, 0.00481)
loop_1 = loop_1.lineTo(-0.03532, -0.0219)
loop_1 = loop_1.lineTo(-0.025, -0.03813)
loop_1 = loop_1.threePointArc((-0.01147, -0.04661), (-0.00696, -0.04846))
loop_1 = loop_1.threePointArc((0.00608, -0.04998), (0.0105, -0.0492))
loop_1 = loop_1.lineTo(0.03052, -0.03874)
loop_1 = loop_1.lineTo(0.03501, -0.0034)
loop_1 = loop_1.lineTo(0.04053, 0.01433)
loop_1 = loop_1.threePointArc((0.03617, 0.02799), (0.03394, 0.03227))
loop_1 = loop_1.threePointArc((0.02307, 0.04295), (0.01857, 0.04549))
loop_1 = loop_1.lineTo(0.00116, 0.04984)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_037/PART_037.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_037/PART_037_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
