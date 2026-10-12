import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.98, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00434, -0.071)
loop_1 = loop_1.circle(0.02045)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.97)

plane_2 = cq.Plane(origin=(0.0, -0.98, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.00434, -0.071)
loop_1 = loop_1.circle(0.02045)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.97)

result = solid_1
result = result.add(solid_2)
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_001/cadfit/raw/part_001/greedy_greedy_test_extrude.stl')
print(f'Successfully exported 2 solids to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_001/cadfit/raw/part_001/greedy_greedy_test_extrude.stl')