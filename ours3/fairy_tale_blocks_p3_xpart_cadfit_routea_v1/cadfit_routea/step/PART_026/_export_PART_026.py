import cadquery as cq
import math
import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.001, -0.64793)
sketch_1 = sketch_1.lineTo(-0.33658, -0.64821)
sketch_1 = sketch_1.threePointArc((-0.35006, -0.64929), (-0.36022, -0.65322))
sketch_1 = sketch_1.lineTo(-0.37984, -0.66597)
sketch_1 = sketch_1.lineTo(-0.39138, -0.68393)
sketch_1 = sketch_1.lineTo(-0.41173, -0.7863)
sketch_1 = sketch_1.threePointArc((-0.41659, -0.82077), (-0.41858, -0.85213))
sketch_1 = sketch_1.threePointArc((-0.42548, -0.90743), (-0.43638, -0.96216))
sketch_1 = sketch_1.lineTo(-0.44483, -0.98111)
sketch_1 = sketch_1.lineTo(-0.47089, -0.99156)
sketch_1 = sketch_1.lineTo(-0.522, -0.99021)
sketch_1 = sketch_1.threePointArc((-0.53062, -0.98613), (-0.53693, -0.98157))
sketch_1 = sketch_1.threePointArc((-0.54094, -0.96146), (-0.53994, -0.94237))
sketch_1 = sketch_1.lineTo(-0.53638, -0.84771)
sketch_1 = sketch_1.threePointArc((-0.52874, -0.78893), (-0.51781, -0.72859))
sketch_1 = sketch_1.threePointArc((-0.50914, -0.67164), (-0.49813, -0.61488))
sketch_1 = sketch_1.threePointArc((-0.48322, -0.52767), (-0.46559, -0.43917))
sketch_1 = sketch_1.threePointArc((-0.45608, -0.39605), (-0.44432, -0.35395))
sketch_1 = sketch_1.threePointArc((-0.43443, -0.34713), (-0.42578, -0.34203))
sketch_1 = sketch_1.threePointArc((-0.39797, -0.34586), (-0.37258, -0.35269))
sketch_1 = sketch_1.lineTo(-0.35988, -0.35583)
sketch_1 = sketch_1.lineTo(-0.34772, -0.35079)
sketch_1 = sketch_1.threePointArc((-0.33966, -0.34006), (-0.33494, -0.32807))
sketch_1 = sketch_1.lineTo(-0.33265, -0.30044)
sketch_1 = sketch_1.threePointArc((-0.33211, -0.28154), (-0.33305, -0.26557))
sketch_1 = sketch_1.lineTo(-0.33179, 0.07083)
sketch_1 = sketch_1.lineTo(-0.33173, 0.1599)
sketch_1 = sketch_1.lineTo(-0.33084, 0.54271)
sketch_1 = sketch_1.lineTo(-0.32924, 0.77119)
sketch_1 = sketch_1.lineTo(-0.32733, 0.98037)
sketch_1 = sketch_1.lineTo(-0.3244, 0.99049)
sketch_1 = sketch_1.lineTo(-0.31417, 0.99828)
sketch_1 = sketch_1.lineTo(-0.001, 0.99829)
sketch_1 = sketch_1.lineTo(-0.001, -0.64793)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.0, -0.098, 0.001), axisEnd=(0.0, 0.902, 0.001))


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fairy_tale_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_026/PART_026.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fairy_tale_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_026/PART_026_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
