import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29762, 0.43333)
loop_1 = loop_1.lineTo(-0.29567, -0.43333)
loop_1 = loop_1.lineTo(0.10714, -0.43236)
loop_1 = loop_1.lineTo(0.10909, 0.19524)
loop_1 = loop_1.lineTo(0.29762, 0.19621)
loop_1 = loop_1.lineTo(0.29665, 0.43333)
loop_1 = loop_1.lineTo(-0.29664, 0.43333)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/smoke10_runs/deepcad__0002_00024054/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/smoke10_runs/deepcad__0002_00024054/sketch_3_interval_0.stl')