import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.57047, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.2948, 0.24609)
loop_1 = loop_1.threePointArc((0.41204, 0.2396), (0.53196, 0.21556))
loop_1 = loop_1.threePointArc((0.59724, 0.19602), (0.66187, 0.17056))
loop_1 = loop_1.threePointArc((0.71464, 0.14944), (0.76606, 0.12329))
loop_1 = loop_1.threePointArc((0.8267, 0.07727), (0.87667, 0.01766))
loop_1 = loop_1.threePointArc((0.9102, -0.05484), (0.92095, -0.13561))
loop_1 = loop_1.lineTo(0.92498, -0.19897)
loop_1 = loop_1.threePointArc((0.91577, -0.21993), (0.89472, -0.22718))
loop_1 = loop_1.threePointArc((0.87259, -0.22653), (0.85171, -0.22086))
loop_1 = loop_1.threePointArc((0.77198, -0.19253), (0.6952, -0.17093))
loop_1 = loop_1.threePointArc((0.61022, -0.14255), (0.52557, -0.10744))
loop_1 = loop_1.threePointArc((0.43188, -0.07749), (0.34065, -0.05974))
loop_1 = loop_1.lineTo(0.22938, -0.05006)
loop_1 = loop_1.threePointArc((0.18279, -0.05084), (0.13954, -0.05389))
loop_1 = loop_1.lineTo(0.01274, -0.05179)
loop_1 = loop_1.threePointArc((-0.05295, -0.05756), (-0.11433, -0.06589))
loop_1 = loop_1.threePointArc((-0.19012, -0.0766), (-0.26096, -0.09028))
loop_1 = loop_1.threePointArc((-0.34471, -0.10395), (-0.43076, -0.11548))
loop_1 = loop_1.threePointArc((-0.51762, -0.13041), (-0.60732, -0.14115))
loop_1 = loop_1.threePointArc((-0.68635, -0.14661), (-0.7672, -0.15133))
loop_1 = loop_1.threePointArc((-0.82254, -0.14885), (-0.87804, -0.13977))
loop_1 = loop_1.threePointArc((-0.90479, -0.13779), (-0.93047, -0.13246))
loop_1 = loop_1.threePointArc((-0.96326, -0.10909), (-0.97722, -0.07109))
loop_1 = loop_1.threePointArc((-0.97739, -0.01628), (-0.96853, 0.03862))
loop_1 = loop_1.threePointArc((-0.9066, 0.14902), (-0.79873, 0.222))
loop_1 = loop_1.threePointArc((-0.72828, 0.24053), (-0.65383, 0.24302))
loop_1 = loop_1.threePointArc((-0.27214, 0.24228), (0.09281, 0.24519))
loop_1 = loop_1.lineTo(0.29337, 0.24617)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.14)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/coast_guard_boat_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_000/PART_000.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/coast_guard_boat_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_000/PART_000_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
