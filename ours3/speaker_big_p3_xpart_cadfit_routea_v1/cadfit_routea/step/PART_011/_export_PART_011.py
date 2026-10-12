import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.39, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15283, 0.9952)
loop_1 = loop_1.lineTo(0.91545, 0.99222)
loop_1 = loop_1.lineTo(0.91072, -0.99973)
loop_1 = loop_1.lineTo(-0.91527, -0.99643)
loop_1 = loop_1.lineTo(-0.91106, 0.99446)
loop_1 = loop_1.lineTo(0.15016, 0.99517)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.78)
plane_2 = cq.Plane(origin=(0.00235, -0.91415, -0.02565), normal=(-0.0001, 1.0, 0.0), xDir=(1.0, 0.0001, -0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.37091, 0.96944)
loop_1 = loop_1.lineTo(-0.39144, 0.96883)
loop_1 = loop_1.lineTo(-0.39132, -1.02103)
loop_1 = loop_1.lineTo(0.3818, -1.0254)
loop_1 = loop_1.lineTo(0.38928, 0.96705)
loop_1 = loop_1.lineTo(0.37091, 0.96944)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.83)

result = solid_1
result = result.add(solid_2)

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/speaker_big_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_011/PART_011.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/speaker_big_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_011/PART_011_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
