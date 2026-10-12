import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.52381, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.6878, 0.61263)
loop_1 = loop_1.lineTo(0.9973, 0.6099)
loop_1 = loop_1.lineTo(0.998, -0.61047)
loop_1 = loop_1.lineTo(-0.99773, -0.60739)
loop_1 = loop_1.lineTo(-0.99658, 0.48683)
loop_1 = loop_1.threePointArc((-0.20018, 0.48738), (0.56341, 0.48891))
loop_1 = loop_1.lineTo(0.64902, 0.49327)
loop_1 = loop_1.threePointArc((0.61843, 0.49543), (0.59219, 0.49431))
loop_1 = loop_1.threePointArc((0.5663, 0.4995), (0.54408, 0.4996))
loop_1 = loop_1.threePointArc((0.51978, 0.50125), (0.4981, 0.50459))
loop_1 = loop_1.threePointArc((0.48453, 0.50482), (0.47491, 0.50496))
loop_1 = loop_1.threePointArc((0.41307, 0.5112), (0.35407, 0.51376))
loop_1 = loop_1.threePointArc((0.33439, 0.51555), (0.31765, 0.51819))
loop_1 = loop_1.lineTo(0.24114, 0.52182)
loop_1 = loop_1.threePointArc((0.20651, 0.52233), (0.17408, 0.52478))
loop_1 = loop_1.threePointArc((0.0952, 0.52179), (0.01663, 0.52352))
loop_1 = loop_1.threePointArc((-0.03235, 0.52373), (-0.07553, 0.52298))
loop_1 = loop_1.lineTo(-0.17399, 0.52532)
loop_1 = loop_1.threePointArc((-0.19459, 0.52508), (-0.21218, 0.52713))
loop_1 = loop_1.threePointArc((-0.27205, 0.52741), (-0.32644, 0.52596))
loop_1 = loop_1.lineTo(-0.36643, 0.52721)
loop_1 = loop_1.threePointArc((-0.39339, 0.52565), (-0.41803, 0.5264))
loop_1 = loop_1.threePointArc((-0.46676, 0.52542), (-0.51418, 0.52829))
loop_1 = loop_1.threePointArc((-0.52848, 0.52793), (-0.53916, 0.52775))
loop_1 = loop_1.threePointArc((-0.5858, 0.52902), (-0.63161, 0.53135))
loop_1 = loop_1.lineTo(-0.70781, 0.52786)
loop_1 = loop_1.lineTo(-0.71924, 0.52632)
loop_1 = loop_1.threePointArc((-0.74853, 0.52862), (-0.77331, 0.52833))
loop_1 = loop_1.threePointArc((-0.80964, 0.53147), (-0.8414, 0.53098))
loop_1 = loop_1.lineTo(-0.85798, 0.53205)
loop_1 = loop_1.lineTo(-0.89282, 0.539)
loop_1 = loop_1.threePointArc((-0.9152, 0.53805), (-0.93532, 0.53936))
loop_1 = loop_1.lineTo(-0.96593, 0.53872)
loop_1 = loop_1.lineTo(-0.99165, 0.52883)
loop_1 = loop_1.lineTo(-0.99754, 0.54457)
loop_1 = loop_1.threePointArc((-0.99835, 0.57363), (-0.99816, 0.60391))
loop_1 = loop_1.lineTo(-0.69021, 0.61263)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/birdhouse_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_021/PART_021.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/birdhouse_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_021/PART_021_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
