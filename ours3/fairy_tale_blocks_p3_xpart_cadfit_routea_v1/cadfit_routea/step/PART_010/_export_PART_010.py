import cadquery as cq
import math
import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(-0.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(0.01128, -0.98464)
sketch_1 = sketch_1.lineTo(-0.00377, -0.9684)
sketch_1 = sketch_1.threePointArc((-0.00922, -0.95775), (-0.01525, -0.9499))
sketch_1 = sketch_1.lineTo(-0.02406, -0.92028)
sketch_1 = sketch_1.lineTo(-0.03026, -0.87543)
sketch_1 = sketch_1.threePointArc((-0.03621, -0.74598), (-0.03513, -0.6125))
sketch_1 = sketch_1.threePointArc((-0.0378, -0.52979), (-0.04276, -0.45216))
sketch_1 = sketch_1.lineTo(-0.06267, -0.0511)
sketch_1 = sketch_1.threePointArc((-0.06366, -0.00907), (-0.06588, 0.02964))
sketch_1 = sketch_1.threePointArc((-0.07391, 0.0435), (-0.08382, 0.0533))
sketch_1 = sketch_1.threePointArc((-0.09875, 0.07486), (-0.10929, 0.0981))
sketch_1 = sketch_1.threePointArc((-0.14413, 0.17616), (-0.17565, 0.25725))
sketch_1 = sketch_1.threePointArc((-0.20475, 0.32501), (-0.23456, 0.38856))
sketch_1 = sketch_1.threePointArc((-0.24218, 0.4001), (-0.25039, 0.40833))
sketch_1 = sketch_1.threePointArc((-0.27467, 0.43035), (-0.28521, 0.46124))
sketch_1 = sketch_1.threePointArc((-0.29135, 0.49911), (-0.29448, 0.53712))
sketch_1 = sketch_1.threePointArc((-0.29198, 0.54716), (-0.28782, 0.55527))
sketch_1 = sketch_1.threePointArc((-0.28, 0.56198), (-0.27146, 0.56518))
sketch_1 = sketch_1.lineTo(-0.23098, 0.5674)
sketch_1 = sketch_1.threePointArc((-0.22682, 0.76939), (-0.22744, 0.97041))
sketch_1 = sketch_1.lineTo(-0.22497, 0.98335)
sketch_1 = sketch_1.threePointArc((-0.2191, 0.99107), (-0.21042, 0.99625))
sketch_1 = sketch_1.threePointArc((-0.2025, 0.99838), (-0.19436, 0.99817))
sketch_1 = sketch_1.lineTo(-0.00602, 0.99829)
sketch_1 = sketch_1.lineTo(0.01128, -0.98464)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.003, 0.108, 0.001), axisEnd=(-0.006, 1.1079999999999999, 0.001))

result = solid_revolve_1

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fairy_tale_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_010/PART_010.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fairy_tale_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_010/PART_010_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
