import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.27177, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01373, 0.99471)
loop_1 = loop_1.threePointArc((0.00639, 0.99019), (0.00187, 0.98324))
loop_1 = loop_1.threePointArc((-0.00628, 0.93298), (-0.00694, 0.88532))
loop_1 = loop_1.threePointArc((-0.01342, 0.75652), (-0.01651, 0.63404))
loop_1 = loop_1.lineTo(-0.03045, 0.30414)
loop_1 = loop_1.threePointArc((-0.03805, 0.10083), (-0.03816, -0.09319))
loop_1 = loop_1.threePointArc((-0.03943, -0.31135), (-0.03664, -0.51935))
loop_1 = loop_1.threePointArc((-0.03659, -0.62095), (-0.03865, -0.72539))
loop_1 = loop_1.threePointArc((-0.03726, -0.81642), (-0.03859, -0.90975))
loop_1 = loop_1.threePointArc((-0.03498, -0.94249), (-0.03039, -0.97241))
loop_1 = loop_1.threePointArc((-0.0256, -0.98446), (-0.01685, -0.99144))
loop_1 = loop_1.threePointArc((-0.00489, -0.99358), (0.00078, -0.9919))
loop_1 = loop_1.lineTo(0.00854, -0.97939)
loop_1 = loop_1.lineTo(0.01438, -0.89439)
loop_1 = loop_1.threePointArc((0.02643, -0.58153), (0.03054, -0.28221))
loop_1 = loop_1.threePointArc((0.03463, -0.04424), (0.03566, 0.183))
loop_1 = loop_1.lineTo(0.03884, 0.61098)
loop_1 = loop_1.threePointArc((0.04071, 0.76538), (0.03807, 0.91237))
loop_1 = loop_1.lineTo(0.03296, 0.97944)
loop_1 = loop_1.lineTo(0.02657, 0.99205)
loop_1 = loop_1.lineTo(0.01496, 0.99458)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.56)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asus_sabertooth_z97_mark_1_motherboard_atx_lga1150_socket_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_000/PART_000.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asus_sabertooth_z97_mark_1_motherboard_atx_lga1150_socket_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_000/PART_000_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
