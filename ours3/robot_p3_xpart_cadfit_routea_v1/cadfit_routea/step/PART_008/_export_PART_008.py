import cadquery as cq
import math
import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.93255, -0.01199)
sketch_1 = sketch_1.threePointArc((0.92935, -0.0751), (0.92379, -0.14067))
sketch_1 = sketch_1.threePointArc((0.9148, -0.24538), (0.89604, -0.35109))
sketch_1 = sketch_1.threePointArc((0.8686, -0.44286), (0.83608, -0.53499))
sketch_1 = sketch_1.threePointArc((0.82318, -0.56459), (0.80844, -0.5925))
sketch_1 = sketch_1.threePointArc((0.74297, -0.69601), (0.65617, -0.78663))
sketch_1 = sketch_1.threePointArc((0.58484, -0.84111), (0.50692, -0.88878))
sketch_1 = sketch_1.threePointArc((0.40347, -0.9356), (0.29207, -0.96818))
sketch_1 = sketch_1.threePointArc((0.21525, -0.981), (0.13715, -0.99279))
sketch_1 = sketch_1.threePointArc((0.09203, -0.99526), (0.04714, -0.99285))
sketch_1 = sketch_1.threePointArc((-0.0017, -0.98971), (-0.05025, -0.98387))
sketch_1 = sketch_1.threePointArc((-0.11449, -0.97645), (-0.1786, -0.96493))
sketch_1 = sketch_1.lineTo(-0.225, -0.95098)
sketch_1 = sketch_1.threePointArc((-0.3699, -0.88886), (-0.50944, -0.80634))
sketch_1 = sketch_1.threePointArc((-0.63543, -0.69613), (-0.74609, -0.56424))
sketch_1 = sketch_1.threePointArc((-0.78721, -0.49881), (-0.82547, -0.43053))
sketch_1 = sketch_1.threePointArc((-0.85334, -0.36538), (-0.87628, -0.29742))
sketch_1 = sketch_1.threePointArc((-0.89962, -0.21585), (-0.9134, -0.13075))
sketch_1 = sketch_1.threePointArc((-0.91993, -0.09068), (-0.92367, -0.05069))
sketch_1 = sketch_1.threePointArc((-0.9283, -0.01488), (-0.93051, 0.02054))
sketch_1 = sketch_1.lineTo(0.93255, -0.01199)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.032, 0.005, 0.001), axisEnd=(-0.968, 0.022000000000000002, 0.001))


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/robot_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_008/PART_008.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/robot_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_008/PART_008_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
