import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.33852, 0.78893)
loop_1 = loop_1.lineTo(0.85115, 0.09814)
loop_1 = loop_1.lineTo(0.51057, -0.68804)
loop_1 = loop_1.lineTo(-0.34058, -0.78618)
loop_1 = loop_1.lineTo(-0.85115, -0.09814)
loop_1 = loop_1.lineTo(-0.51057, 0.68804)
loop_1 = loop_1.lineTo(0.33682, 0.78873)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0049_00493354/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0049_00493354/sketch_0_interval_0.stl')