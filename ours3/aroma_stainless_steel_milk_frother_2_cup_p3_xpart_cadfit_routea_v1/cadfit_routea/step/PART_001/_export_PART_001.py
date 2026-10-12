import cadquery as cq
import math
import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(0.0, -0.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(-0.34412, 0.98817)
sketch_1 = sketch_1.lineTo(-0.30562, 0.98208)
sketch_1 = sketch_1.threePointArc((-0.29047, 0.98012), (-0.27789, 0.97502))
sketch_1 = sketch_1.threePointArc((-0.25997, 0.96383), (-0.24292, 0.95756))
sketch_1 = sketch_1.threePointArc((-0.11201, 0.95287), (0.01176, 0.95103))
sketch_1 = sketch_1.lineTo(-0.00441, -0.9011)
sketch_1 = sketch_1.lineTo(-0.43343, -0.9037)
sketch_1 = sketch_1.threePointArc((-0.47699, -0.91025), (-0.51439, -0.92511))
sketch_1 = sketch_1.lineTo(-0.57038, -0.94976)
sketch_1 = sketch_1.lineTo(-0.60498, -0.96919)
sketch_1 = sketch_1.lineTo(-0.61648, -0.97255)
sketch_1 = sketch_1.lineTo(-0.62687, -0.96958)
sketch_1 = sketch_1.threePointArc((-0.63118, -0.96265), (-0.63379, -0.95696))
sketch_1 = sketch_1.threePointArc((-0.63113, -0.94889), (-0.62856, -0.94279))
sketch_1 = sketch_1.lineTo(-0.59373, -0.90991)
sketch_1 = sketch_1.lineTo(-0.58952, -0.88204)
sketch_1 = sketch_1.threePointArc((-0.58153, -0.45433), (-0.57669, -0.04576))
sketch_1 = sketch_1.threePointArc((-0.57351, 0.04667), (-0.56923, 0.14059))
sketch_1 = sketch_1.lineTo(-0.5669, 0.15378)
sketch_1 = sketch_1.lineTo(-0.57137, 0.17076)
sketch_1 = sketch_1.threePointArc((-0.57121, 0.23346), (-0.56748, 0.29647))
sketch_1 = sketch_1.threePointArc((-0.56846, 0.38022), (-0.57098, 0.45859))
sketch_1 = sketch_1.threePointArc((-0.57093, 0.55945), (-0.57451, 0.65403))
sketch_1 = sketch_1.lineTo(-0.57906, 0.80211)
sketch_1 = sketch_1.threePointArc((-0.58172, 0.85398), (-0.58598, 0.90151))
sketch_1 = sketch_1.threePointArc((-0.59433, 0.90949), (-0.60098, 0.9152))
sketch_1 = sketch_1.threePointArc((-0.6062, 0.92797), (-0.60883, 0.93982))
sketch_1 = sketch_1.threePointArc((-0.60697, 0.95094), (-0.60585, 0.9595))
sketch_1 = sketch_1.lineTo(-0.56271, 0.97321)
sketch_1 = sketch_1.threePointArc((-0.55091, 0.97746), (-0.53814, 0.98023))
sketch_1 = sketch_1.threePointArc((-0.51875, 0.97767), (-0.50122, 0.97353))
sketch_1 = sketch_1.lineTo(-0.43589, 0.97549)
sketch_1 = sketch_1.lineTo(-0.42572, 0.97741)
sketch_1 = sketch_1.threePointArc((-0.40079, 0.98154), (-0.37459, 0.98402))
sketch_1 = sketch_1.lineTo(-0.36244, 0.98642)
sketch_1 = sketch_1.lineTo(-0.35021, 0.98656)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.004, 0.0, 0.001), axisEnd=(0.013000000000000001, 1.0, 0.001))

result = solid_revolve_1

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/aroma_stainless_steel_milk_frother_2_cup_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/aroma_stainless_steel_milk_frother_2_cup_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
