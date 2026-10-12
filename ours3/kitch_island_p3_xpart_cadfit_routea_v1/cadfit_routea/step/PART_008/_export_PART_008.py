import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.57152, 0.0211)
loop_1 = loop_1.lineTo(0.58178, 0.01819)
loop_1 = loop_1.lineTo(0.58447, -0.01425)
loop_1 = loop_1.threePointArc((0.56887, -0.02089), (0.5584, -0.02059))
loop_1 = loop_1.lineTo(-0.58122, -0.0187)
loop_1 = loop_1.threePointArc((-0.58582, -0.00229), (-0.58542, 0.00988))
loop_1 = loop_1.threePointArc((-0.5756, 0.02002), (-0.57089, 0.02104))
loop_1 = loop_1.lineTo(0.57071, 0.0211)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_008/PART_008.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/kitch_island_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_008/PART_008_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
