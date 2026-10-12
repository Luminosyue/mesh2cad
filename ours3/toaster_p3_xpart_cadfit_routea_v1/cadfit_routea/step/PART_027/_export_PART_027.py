import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.98), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.15696, 0.00971)
loop_1 = loop_1.lineTo(-0.15287, -0.00145)
loop_1 = loop_1.lineTo(-0.13833, -0.01209)
loop_1 = loop_1.lineTo(-0.12694, -0.01485)
loop_1 = loop_1.lineTo(-0.11675, -0.01966)
loop_1 = loop_1.lineTo(-0.10966, -0.03425)
loop_1 = loop_1.lineTo(-0.0949, -0.04919)
loop_1 = loop_1.lineTo(-0.08403, -0.05217)
loop_1 = loop_1.threePointArc((-0.07152, -0.05275), (-0.05975, -0.05243))
loop_1 = loop_1.threePointArc((-0.02655, -0.05209), (0.00778, -0.05197))
loop_1 = loop_1.threePointArc((0.03267, -0.05179), (0.05633, -0.0514))
loop_1 = loop_1.lineTo(0.06646, -0.04919)
loop_1 = loop_1.lineTo(0.0771, -0.04407)
loop_1 = loop_1.threePointArc((0.08392, -0.0375), (0.0901, -0.03116))
loop_1 = loop_1.lineTo(0.10993, -0.01708)
loop_1 = loop_1.threePointArc((0.12053, -0.01407), (0.13147, -0.01143))
loop_1 = loop_1.lineTo(0.14175, -0.00753)
loop_1 = loop_1.lineTo(0.15244, -0.00085)
loop_1 = loop_1.lineTo(0.16067, 0.0102)
loop_1 = loop_1.lineTo(0.16309, 0.02095)
loop_1 = loop_1.lineTo(0.16228, 0.03143)
loop_1 = loop_1.lineTo(0.1549, 0.0424)
loop_1 = loop_1.lineTo(0.14036, 0.05072)
loop_1 = loop_1.lineTo(0.12907, 0.0526)
loop_1 = loop_1.threePointArc((0.11557, 0.05302), (0.10285, 0.05309))
loop_1 = loop_1.threePointArc((0.07018, 0.05347), (0.03905, 0.05322))
loop_1 = loop_1.threePointArc((0.01088, 0.05331), (-0.01821, 0.05352))
loop_1 = loop_1.lineTo(-0.04725, 0.05353)
loop_1 = loop_1.lineTo(-0.09127, 0.05378)
loop_1 = loop_1.threePointArc((-0.10086, 0.05365), (-0.10982, 0.05324))
loop_1 = loop_1.lineTo(-0.12873, 0.0495)
loop_1 = loop_1.lineTo(-0.13931, 0.04423)
loop_1 = loop_1.threePointArc((-0.15005, 0.03416), (-0.15268, 0.03038))
loop_1 = loop_1.lineTo(-0.15629, 0.01995)
loop_1 = loop_1.lineTo(-0.15696, 0.00971)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.95)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_027/PART_027.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_027/PART_027_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
