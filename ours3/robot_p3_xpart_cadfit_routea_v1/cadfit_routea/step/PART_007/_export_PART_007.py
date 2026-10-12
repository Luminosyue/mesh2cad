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

sketch_1 = sketch_1.moveTo(-0.92761, -0.00024)
sketch_1 = sketch_1.threePointArc((-0.92199, -0.13117), (-0.90991, -0.25641))
sketch_1 = sketch_1.threePointArc((-0.87275, -0.41711), (-0.81404, -0.56318))
sketch_1 = sketch_1.threePointArc((-0.7955, -0.60255), (-0.77584, -0.63716))
sketch_1 = sketch_1.threePointArc((-0.7015, -0.73473), (-0.61852, -0.81545))
sketch_1 = sketch_1.threePointArc((-0.55393, -0.86102), (-0.4907, -0.89922))
sketch_1 = sketch_1.threePointArc((-0.38293, -0.94476), (-0.27658, -0.97395))
sketch_1 = sketch_1.threePointArc((-0.18008, -0.99187), (-0.0882, -1.00023))
sketch_1 = sketch_1.threePointArc((0.00332, -0.99704), (0.08848, -0.98582))
sketch_1 = sketch_1.threePointArc((0.16698, -0.97157), (0.23919, -0.95257))
sketch_1 = sketch_1.threePointArc((0.36903, -0.89719), (0.48423, -0.82953))
sketch_1 = sketch_1.threePointArc((0.54266, -0.78947), (0.59364, -0.74749))
sketch_1 = sketch_1.threePointArc((0.67993, -0.66973), (0.74768, -0.58364))
sketch_1 = sketch_1.threePointArc((0.80433, -0.49002), (0.8485, -0.39477))
sketch_1 = sketch_1.threePointArc((0.86831, -0.347), (0.88278, -0.30156))
sketch_1 = sketch_1.threePointArc((0.9077, -0.21425), (0.92224, -0.13028))
sketch_1 = sketch_1.threePointArc((0.9264, -0.06299), (0.9277, -0.00024))
sketch_1 = sketch_1.lineTo(-0.92761, -0.00024)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.020999999999999998, 0.001, 0.001), axisEnd=(-1.0210000000000001, 0.001, 0.001))


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/robot_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_007/PART_007.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/robot_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_007/PART_007_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
