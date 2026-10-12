import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.98, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.22183, 0.77848)
loop_1 = loop_1.lineTo(0.22869, 0.76813)
loop_1 = loop_1.threePointArc((0.23178, 0.73977), (0.23312, 0.71008))
loop_1 = loop_1.threePointArc((0.23792, 0.58927), (0.23766, 0.46444))
loop_1 = loop_1.lineTo(0.22497, 0.12403)
loop_1 = loop_1.threePointArc((0.22379, -0.03268), (0.22778, -0.18206))
loop_1 = loop_1.threePointArc((0.23375, -0.34066), (0.23814, -0.50482))
loop_1 = loop_1.threePointArc((0.23584, -0.64094), (0.22333, -0.78106))
loop_1 = loop_1.lineTo(0.19936, -0.78438)
loop_1 = loop_1.threePointArc((0.19573, -0.76784), (0.19636, -0.75127))
loop_1 = loop_1.lineTo(0.20546, -0.53704)
loop_1 = loop_1.lineTo(0.20514, -0.35901)
loop_1 = loop_1.threePointArc((0.20116, -0.25565), (0.19856, -0.14898))
loop_1 = loop_1.threePointArc((0.19607, -0.04625), (0.19777, 0.05965))
loop_1 = loop_1.threePointArc((0.1995, 0.22466), (0.20763, 0.39522))
loop_1 = loop_1.threePointArc((0.2088, 0.46315), (0.20579, 0.52728))
loop_1 = loop_1.lineTo(0.19906, 0.70359)
loop_1 = loop_1.threePointArc((0.19762, 0.73705), (0.19897, 0.77083))
loop_1 = loop_1.lineTo(0.22183, 0.77848)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.97)
result = solid_1

# ===== Operation Script =====
plane_op_1 = cq.Plane(origin=(0.0, 0.0, -0.77705), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_op_1 = cq.Workplane(plane_op_1)
loop_1 = sketch_op_1.moveTo(-0.22313, -0.99)
loop_1 = loop_1.lineTo(-0.19633, -0.98932)
loop_1 = loop_1.lineTo(-0.19728, -0.02837)
loop_1 = loop_1.threePointArc((-0.19964, -0.08088), (-0.2033, -0.1348))
loop_1 = loop_1.threePointArc((-0.20804, -0.23253), (-0.20919, -0.32581))
loop_1 = loop_1.threePointArc((-0.21077, -0.47295), (-0.21079, -0.61355))
loop_1 = loop_1.threePointArc((-0.21271, -0.71205), (-0.21238, -0.80599))
loop_1 = loop_1.threePointArc((-0.21389, -0.85445), (-0.21633, -0.90415))
loop_1 = loop_1.threePointArc((-0.2167, -0.94177), (-0.21665, -0.97721))
loop_1 = loop_1.lineTo(-0.22313, -0.99)
loop_1 = loop_1.close()
sketch_op_1=sketch_op_1.add(loop_1)
solid_op_1 = sketch_op_1.extrude(1.56)
result_op = solid_op_1

# ===== Combine using cut =====
final_result = result.cut(result_op)


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asus_x99deluxe_motherboard_atx_lga2011v3_socket_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_002/PART_002.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asus_x99deluxe_motherboard_atx_lga2011v3_socket_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_002/PART_002_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
