import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.04), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 1.0)
loop_1 = loop_1.lineTo(-0.99468, -1.0)
loop_1 = loop_1.lineTo(1.0, -0.99468)
loop_1 = loop_1.lineTo(0.99468, 1.0)
loop_1 = loop_1.lineTo(-0.99733, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/full_runs/0003_00033880/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/full_runs/0003_00033880/sketch_12_interval_0.stl')