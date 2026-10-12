import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.51764), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.86065, -0.31112)
loop_1 = loop_1.threePointArc((-0.85534, -0.34661), (-0.84323, -0.37888))
loop_1 = loop_1.threePointArc((-0.82594, -0.39858), (-0.80671, -0.41228))
loop_1 = loop_1.threePointArc((-0.75228, -0.42418), (-0.70007, -0.42716))
loop_1 = loop_1.threePointArc((-0.45229, -0.43427), (-0.21567, -0.43868))
loop_1 = loop_1.threePointArc((0.13518, -0.44606), (0.47066, -0.44995))
loop_1 = loop_1.threePointArc((0.58196, -0.45178), (0.69641, -0.45448))
loop_1 = loop_1.threePointArc((0.7445, -0.45237), (0.78912, -0.44819))
loop_1 = loop_1.threePointArc((0.82138, -0.43877), (0.84857, -0.42435))
loop_1 = loop_1.threePointArc((0.85975, -0.41191), (0.86637, -0.39887))
loop_1 = loop_1.threePointArc((0.87337, -0.38358), (0.87596, -0.36903))
loop_1 = loop_1.threePointArc((0.87549, -0.3478), (0.87101, -0.32923))
loop_1 = loop_1.threePointArc((0.84459, -0.25458), (0.80978, -0.18859))
loop_1 = loop_1.threePointArc((0.76127, -0.11823), (0.70946, -0.05647))
loop_1 = loop_1.lineTo(0.6691, -0.01314)
loop_1 = loop_1.threePointArc((0.57842, 0.07254), (0.48966, 0.15088))
loop_1 = loop_1.lineTo(0.41321, 0.21987)
loop_1 = loop_1.threePointArc((0.37084, 0.25442), (0.3295, 0.2843))
loop_1 = loop_1.lineTo(0.26697, 0.33027)
loop_1 = loop_1.lineTo(0.22327, 0.35485)
loop_1 = loop_1.threePointArc((0.17629, 0.37574), (0.12941, 0.39835))
loop_1 = loop_1.threePointArc((0.08524, 0.41467), (0.04315, 0.42673))
loop_1 = loop_1.lineTo(-0.04884, 0.43582)
loop_1 = loop_1.threePointArc((-0.10652, 0.43203), (-0.15985, 0.42249))
loop_1 = loop_1.threePointArc((-0.22986, 0.40883), (-0.29417, 0.38963))
loop_1 = loop_1.threePointArc((-0.36389, 0.35826), (-0.4287, 0.32691))
loop_1 = loop_1.threePointArc((-0.47556, 0.30032), (-0.51794, 0.27343))
loop_1 = loop_1.threePointArc((-0.55993, 0.23977), (-0.59666, 0.20553))
loop_1 = loop_1.threePointArc((-0.62034, 0.18239), (-0.64045, 0.15956))
loop_1 = loop_1.threePointArc((-0.69361, 0.09714), (-0.73404, 0.03131))
loop_1 = loop_1.threePointArc((-0.76771, -0.02888), (-0.79418, -0.08909))
loop_1 = loop_1.lineTo(-0.82399, -0.16146)
loop_1 = loop_1.threePointArc((-0.84251, -0.21956), (-0.85423, -0.27549))
loop_1 = loop_1.threePointArc((-0.85882, -0.29346), (-0.8609, -0.30967))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.0)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/baby_car_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_006/PART_006.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/baby_car_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_006/PART_006_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
