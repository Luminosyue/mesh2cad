import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01181, 0.20579, -0.00731), normal=(-0.00077, -1.0, 0.00076), xDir=(-1.0, 0.00077, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.82307, 0.89649)
loop_1 = loop_1.lineTo(0.74921, 0.8963)
loop_1 = loop_1.lineTo(-0.24084, 0.88711)
loop_1 = loop_1.lineTo(-0.94987, 0.87763)
loop_1 = loop_1.threePointArc((-0.97699, 0.87651), (-0.99342, 0.87452))
loop_1 = loop_1.lineTo(-1.01128, 0.84642)
loop_1 = loop_1.lineTo(-1.01107, -0.88935)
loop_1 = loop_1.lineTo(-1.0009, -0.90285)
loop_1 = loop_1.lineTo(-0.97065, -0.91036)
loop_1 = loop_1.threePointArc((-0.80537, -0.91194), (-0.64674, -0.90818))
loop_1 = loop_1.threePointArc((-0.30777, -0.9077), (0.04284, -0.9117))
loop_1 = loop_1.threePointArc((0.49744, -0.90586), (0.96368, -0.90717))
loop_1 = loop_1.lineTo(0.98033, -0.89654)
loop_1 = loop_1.lineTo(0.98694, -0.88373)
loop_1 = loop_1.lineTo(0.98438, 0.88072)
loop_1 = loop_1.lineTo(0.97306, 0.88876)
loop_1 = loop_1.lineTo(0.96117, 0.89269)
loop_1 = loop_1.threePointArc((0.88909, 0.89626), (0.82851, 0.89599))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.41)
plane_2 = cq.Plane(origin=(-0.9908, 0.00611, -0.00365), normal=(1.0, -0.00062, 0.0004), xDir=(-0.00062, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.17579, 0.88207)
loop_1 = loop_1.lineTo(-0.20003, 0.88139)
loop_1 = loop_1.lineTo(-0.21184, 0.8726)
loop_1 = loop_1.lineTo(-0.20972, -0.89487)
loop_1 = loop_1.lineTo(-0.19508, -0.9054)
loop_1 = loop_1.threePointArc((-0.15326, -0.90669), (-0.11309, -0.90632))
loop_1 = loop_1.threePointArc((0.04438, -0.9069), (0.19179, -0.90619))
loop_1 = loop_1.lineTo(0.20872, -0.90107)
loop_1 = loop_1.lineTo(0.21667, -0.88845)
loop_1 = loop_1.lineTo(0.21719, -0.8659)
loop_1 = loop_1.lineTo(0.22117, 0.81622)
loop_1 = loop_1.threePointArc((0.22178, 0.84358), (0.22114, 0.86508))
loop_1 = loop_1.lineTo(0.19769, 0.88076)
loop_1 = loop_1.lineTo(-0.17093, 0.88205)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.98)

result = solid_1
result = result.add(solid_2)

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asus_m5a99fx_pro_r20_motherboard_atx_socket_am3_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_005/PART_005.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asus_m5a99fx_pro_r20_motherboard_atx_socket_am3_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_005/PART_005_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
