import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04176, -0.05497, -0.07433), normal=(0.0, 1.0, 0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.82961, 0.05225)
loop_1 = loop_1.lineTo(-0.95824, -0.07638)
loop_1 = loop_1.lineTo(-0.95824, -0.20091)
loop_1 = loop_1.lineTo(-0.79313, -0.0358)
loop_1 = loop_1.lineTo(1.04176, -0.0358)
loop_1 = loop_1.lineTo(0.9702, 0.03576)
loop_1 = loop_1.lineTo(0.87666, 0.05225)
loop_1 = loop_1.lineTo(-0.80844, 0.05225)
loop_1 = loop_1.lineTo(-0.82961, 0.05225)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0070_00704087/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0070_00704087/sketch_0_interval_0.stl')