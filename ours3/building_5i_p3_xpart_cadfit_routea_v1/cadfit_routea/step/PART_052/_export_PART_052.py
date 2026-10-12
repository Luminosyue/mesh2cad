import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.94, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.6147, 0.5832)
loop_1 = loop_1.lineTo(0.6279, 0.57829)
loop_1 = loop_1.threePointArc((0.63239, 0.57217), (0.63322, 0.56551))
loop_1 = loop_1.threePointArc((0.6196, 0.53983), (0.60176, 0.52215))
loop_1 = loop_1.threePointArc((0.5355, 0.45353), (0.46592, 0.38442))
loop_1 = loop_1.threePointArc((0.3961, 0.3118), (0.321, 0.24015))
loop_1 = loop_1.threePointArc((0.30427, 0.22177), (0.28582, 0.20565))
loop_1 = loop_1.threePointArc((0.27081, 0.19681), (0.2585, 0.18733))
loop_1 = loop_1.lineTo(0.24625, 0.18328)
loop_1 = loop_1.lineTo(0.23537, 0.18204)
loop_1 = loop_1.lineTo(0.21271, 0.16876)
loop_1 = loop_1.threePointArc((0.20421, 0.15489), (0.19451, 0.14261))
loop_1 = loop_1.threePointArc((0.15003, 0.10381), (0.11098, 0.06439))
loop_1 = loop_1.threePointArc((0.06638, 0.02356), (0.01966, -0.01669))
loop_1 = loop_1.lineTo(-0.06868, -0.09675)
loop_1 = loop_1.threePointArc((-0.12817, -0.15433), (-0.18257, -0.21067))
loop_1 = loop_1.lineTo(-0.33961, -0.35338)
loop_1 = loop_1.threePointArc((-0.40804, -0.4182), (-0.47085, -0.48151))
loop_1 = loop_1.threePointArc((-0.5349, -0.53962), (-0.6043, -0.595))
loop_1 = loop_1.threePointArc((-0.61766, -0.60078), (-0.63093, -0.6045))
loop_1 = loop_1.lineTo(-0.64301, -0.59835)
loop_1 = loop_1.lineTo(-0.64095, -0.58526)
loop_1 = loop_1.threePointArc((-0.61864, -0.55898), (-0.59307, -0.53554))
loop_1 = loop_1.threePointArc((-0.562, -0.50646), (-0.53356, -0.47869))
loop_1 = loop_1.lineTo(-0.33068, -0.28693)
loop_1 = loop_1.threePointArc((-0.25251, -0.21519), (-0.18018, -0.14528))
loop_1 = loop_1.threePointArc((-0.10329, -0.07262), (-0.02301, 0.00097))
loop_1 = loop_1.threePointArc((0.06036, 0.0793), (0.13884, 0.15457))
loop_1 = loop_1.lineTo(0.18645, 0.19908)
loop_1 = loop_1.threePointArc((0.20347, 0.20632), (0.22049, 0.21086))
loop_1 = loop_1.lineTo(0.23829, 0.21848)
loop_1 = loop_1.lineTo(0.3549, 0.33356)
loop_1 = loop_1.threePointArc((0.40402, 0.38206), (0.44931, 0.42894))
loop_1 = loop_1.lineTo(0.58403, 0.56096)
loop_1 = loop_1.threePointArc((0.59801, 0.57345), (0.61375, 0.58275))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.57)

result = solid_1

try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_052/PART_052.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_052/PART_052_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
