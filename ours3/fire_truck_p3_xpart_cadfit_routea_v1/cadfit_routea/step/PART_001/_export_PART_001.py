import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.24667, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05006, 0.97982)
loop_1 = loop_1.threePointArc((0.04482, 0.97982), (0.14344, 0.97353))
loop_1 = loop_1.threePointArc((0.25625, 0.95259), (0.36828, 0.91783))
loop_1 = loop_1.threePointArc((0.4604, 0.87313), (0.55115, 0.82148))
loop_1 = loop_1.threePointArc((0.66503, 0.7321), (0.76973, 0.62673))
loop_1 = loop_1.threePointArc((0.82515, 0.55271), (0.87617, 0.47374))
loop_1 = loop_1.threePointArc((0.94347, 0.29914), (0.9883, 0.11185))
loop_1 = loop_1.threePointArc((0.9906, 0.02498), (0.98056, -0.0626))
loop_1 = loop_1.threePointArc((0.97022, -0.14338), (0.95492, -0.22458))
loop_1 = loop_1.lineTo(0.93922, -0.31914)
loop_1 = loop_1.threePointArc((0.92396, -0.36206), (0.90404, -0.40267))
loop_1 = loop_1.threePointArc((0.88475, -0.45387), (0.86139, -0.50331))
loop_1 = loop_1.threePointArc((0.80386, -0.58305), (0.73765, -0.65814))
loop_1 = loop_1.threePointArc((0.67568, -0.72045), (0.60474, -0.77504))
loop_1 = loop_1.threePointArc((0.51713, -0.8365), (0.42051, -0.88767))
loop_1 = loop_1.threePointArc((0.26563, -0.9473), (0.09686, -0.9794))
loop_1 = loop_1.threePointArc((0.00347, -0.98571), (-0.09174, -0.97978))
loop_1 = loop_1.threePointArc((-0.19418, -0.96545), (-0.29696, -0.94109))
loop_1 = loop_1.threePointArc((-0.48597, -0.85982), (-0.65894, -0.73706))
loop_1 = loop_1.threePointArc((-0.71752, -0.68497), (-0.76915, -0.62455))
loop_1 = loop_1.threePointArc((-0.84111, -0.5348), (-0.89503, -0.43034))
loop_1 = loop_1.threePointArc((-0.94299, -0.30357), (-0.97902, -0.17022))
loop_1 = loop_1.threePointArc((-0.99102, -0.01574), (-0.98279, 0.14319))
loop_1 = loop_1.threePointArc((-0.9581, 0.25708), (-0.92053, 0.37012))
loop_1 = loop_1.threePointArc((-0.87919, 0.45416), (-0.82841, 0.53479))
loop_1 = loop_1.threePointArc((-0.79574, 0.58496), (-0.75602, 0.63011))
loop_1 = loop_1.threePointArc((-0.68665, 0.70421), (-0.60613, 0.77188))
loop_1 = loop_1.threePointArc((-0.50711, 0.84306), (-0.39883, 0.90534))
loop_1 = loop_1.threePointArc((-0.26263, 0.94738), (-0.11931, 0.97613))
loop_1 = loop_1.threePointArc((-0.08483, 0.97854), (-0.05109, 0.98029))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fire_truck_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/fire_truck_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_001/PART_001_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
