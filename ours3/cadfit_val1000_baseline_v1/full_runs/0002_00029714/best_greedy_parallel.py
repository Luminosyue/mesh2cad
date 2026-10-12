import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.25, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.625)
loop_1 = loop_1.lineTo(-0.99567, -0.625)
loop_1 = loop_1.lineTo(1.0, -0.62067)
loop_1 = loop_1.lineTo(0.99567, 0.625)
loop_1 = loop_1.lineTo(-0.99783, 0.625)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/full_runs/0002_00029714/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/full_runs/0002_00029714/sketch_5_interval_0.stl')