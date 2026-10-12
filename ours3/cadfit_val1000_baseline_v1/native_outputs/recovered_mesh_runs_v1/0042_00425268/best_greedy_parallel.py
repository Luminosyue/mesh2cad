import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.22143, 0.33667, -0.2295), normal=(0.0, -1.0, -0.0), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77857, 0.7705)
loop_1 = loop_1.lineTo(-1.22143, 0.7705)
loop_1 = loop_1.lineTo(-1.22143, 0.10383)
loop_1 = loop_1.lineTo(-0.55476, 0.10383)
loop_1 = loop_1.lineTo(-0.55476, -0.56283)
loop_1 = loop_1.lineTo(0.1119, -0.56283)
loop_1 = loop_1.lineTo(0.1119, -1.2295)
loop_1 = loop_1.lineTo(0.77857, -1.2295)
loop_1 = loop_1.lineTo(0.77857, 0.76425)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.67)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0042_00425268/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0042_00425268/sketch_6_interval_0.stl')