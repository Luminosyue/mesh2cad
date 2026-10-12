import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.12349, 0.17149, 1.0), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.70149, 0.54651)
loop_1 = loop_1.lineTo(0.70149, 0.36651)
loop_1 = loop_1.lineTo(-0.17851, 0.36651)
loop_1 = loop_1.lineTo(-0.17851, -0.61349)
loop_1 = loop_1.lineTo(0.70149, -0.61462)
loop_1 = loop_1.lineTo(0.70149, -0.79349)
loop_1 = loop_1.lineTo(-0.35851, -0.79349)
loop_1 = loop_1.lineTo(-0.35851, 0.54651)
loop_1 = loop_1.lineTo(0.69652, 0.54651)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/full_runs/0000_00002719/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/full_runs/0000_00002719/sketch_8_interval_0.stl')