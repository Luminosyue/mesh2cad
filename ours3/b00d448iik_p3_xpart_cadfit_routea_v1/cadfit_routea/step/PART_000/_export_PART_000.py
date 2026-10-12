import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.99, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00052, 0.32774)
loop_1 = loop_1.lineTo(-0.00943, 0.31207)
loop_1 = loop_1.lineTo(-0.00828, -0.31866)
loop_1 = loop_1.lineTo(0.00949, -0.31862)
loop_1 = loop_1.lineTo(0.00854, 0.31886)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.99)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/b00d448iik_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_000/PART_000.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/b00d448iik_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_000/PART_000_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
