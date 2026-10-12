import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.8), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34967, -0.05363)
loop_1 = loop_1.lineTo(-0.34877, -0.0854)
loop_1 = loop_1.threePointArc((-0.34581, -0.10814), (-0.33848, -0.12812))
loop_1 = loop_1.threePointArc((-0.32055, -0.17005), (-0.30156, -0.20866))
loop_1 = loop_1.threePointArc((-0.29321, -0.2224), (-0.2851, -0.23462))
loop_1 = loop_1.threePointArc((-0.25515, -0.26948), (-0.22483, -0.30047))
loop_1 = loop_1.threePointArc((-0.2063, -0.31695), (-0.18786, -0.3308))
loop_1 = loop_1.threePointArc((-0.14493, -0.35218), (-0.10257, -0.36825))
loop_1 = loop_1.threePointArc((-0.09034, -0.37088), (-0.07916, -0.37224))
loop_1 = loop_1.threePointArc((-0.04164, -0.37775), (-0.00611, -0.38114))
loop_1 = loop_1.threePointArc((0.04128, -0.37801), (0.08596, -0.37399))
loop_1 = loop_1.threePointArc((0.11069, -0.36611), (0.1332, -0.35731))
loop_1 = loop_1.threePointArc((0.15214, -0.35063), (0.16873, -0.34232))
loop_1 = loop_1.threePointArc((0.20083, -0.31945), (0.23023, -0.29738))
loop_1 = loop_1.threePointArc((0.25181, -0.27551), (0.2711, -0.25419))
loop_1 = loop_1.lineTo(0.30205, -0.21864)
loop_1 = loop_1.lineTo(0.3117, -0.20228)
loop_1 = loop_1.threePointArc((0.32237, -0.17474), (0.33145, -0.14868))
loop_1 = loop_1.threePointArc((0.33961, -0.11927), (0.34605, -0.09145))
loop_1 = loop_1.threePointArc((0.34794, -0.07247), (0.34818, -0.05489))
loop_1 = loop_1.lineTo(0.34806, 0.00286)
loop_1 = loop_1.threePointArc((0.34668, 0.02186), (0.343, 0.03902))
loop_1 = loop_1.threePointArc((0.32943, 0.08523), (0.31051, 0.12665))
loop_1 = loop_1.threePointArc((0.28185, 0.16846), (0.25149, 0.2055))
loop_1 = loop_1.threePointArc((0.19962, 0.25059), (0.14727, 0.28947))
loop_1 = loop_1.lineTo(0.11147, 0.31655)
loop_1 = loop_1.lineTo(0.06497, 0.35644)
loop_1 = loop_1.threePointArc((0.05568, 0.36157), (0.0469, 0.36515))
loop_1 = loop_1.threePointArc((0.01818, 0.36973), (-0.009, 0.36989))
loop_1 = loop_1.threePointArc((-0.0345, 0.36828), (-0.05787, 0.36378))
loop_1 = loop_1.threePointArc((-0.08844, 0.35725), (-0.11608, 0.34764))
loop_1 = loop_1.threePointArc((-0.14392, 0.33323), (-0.16912, 0.31829))
loop_1 = loop_1.threePointArc((-0.20593, 0.28654), (-0.23801, 0.2537))
loop_1 = loop_1.threePointArc((-0.2496, 0.23596), (-0.25888, 0.21865))
loop_1 = loop_1.threePointArc((-0.28005, 0.18113), (-0.29795, 0.14465))
loop_1 = loop_1.threePointArc((-0.31394, 0.1157), (-0.32703, 0.08761))
loop_1 = loop_1.threePointArc((-0.33853, 0.0481), (-0.34679, 0.01025))
loop_1 = loop_1.threePointArc((-0.34882, -0.0225), (-0.34956, -0.05328))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.62)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/android_figure_orange_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/android_figure_orange_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_003/PART_003_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
