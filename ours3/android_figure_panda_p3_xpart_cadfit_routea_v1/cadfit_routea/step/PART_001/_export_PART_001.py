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

sketch_1 = sketch_1.moveTo(-0.60946, 0.86993)
sketch_1 = sketch_1.threePointArc((-0.701, 0.8688), (-0.78877, 0.86428))
sketch_1 = sketch_1.threePointArc((-0.86028, 0.84371), (-0.91688, 0.80433))
sketch_1 = sketch_1.threePointArc((-0.95147, 0.75889), (-0.97288, 0.71112))
sketch_1 = sketch_1.threePointArc((-0.9836, 0.64333), (-0.98602, 0.57995))
sketch_1 = sketch_1.threePointArc((-0.9877, 0.50369), (-0.98673, 0.43284))
sketch_1 = sketch_1.threePointArc((-0.98863, 0.34194), (-0.98725, 0.25535))
sketch_1 = sketch_1.threePointArc((-0.98793, 0.1375), (-0.99088, 0.01737))
sketch_1 = sketch_1.threePointArc((-0.99157, -0.0902), (-0.99458, -0.19963))
sketch_1 = sketch_1.lineTo(-0.99317, -0.57182)
sketch_1 = sketch_1.threePointArc((-0.99133, -0.64333), (-0.99135, -0.71715))
sketch_1 = sketch_1.threePointArc((-0.98974, -0.76513), (-0.98733, -0.80876))
sketch_1 = sketch_1.threePointArc((-0.96989, -0.84205), (-0.93892, -0.85571))
sketch_1 = sketch_1.threePointArc((-0.91411, -0.85851), (-0.89081, -0.85758))
sketch_1 = sketch_1.threePointArc((-0.68794, -0.86333), (-0.49382, -0.86465))
sketch_1 = sketch_1.lineTo(-0.13215, -0.8669)
sketch_1 = sketch_1.threePointArc((-0.06696, -0.86469), (-0.00159, -0.86368))
sketch_1 = sketch_1.lineTo(-0.00159, 0.84204)
sketch_1 = sketch_1.threePointArc((-0.11673, 0.84212), (-0.23664, 0.84492))
sketch_1 = sketch_1.threePointArc((-0.35757, 0.85413), (-0.48079, 0.86553))
sketch_1 = sketch_1.threePointArc((-0.54729, 0.86883), (-0.60879, 0.87022))
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.001, -0.013000000000000001, 0.001), axisEnd=(-0.001, 0.987, 0.001))


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/android_figure_panda_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/android_figure_panda_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
