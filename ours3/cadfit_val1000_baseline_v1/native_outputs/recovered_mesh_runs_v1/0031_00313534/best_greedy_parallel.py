import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01482, -0.43143, -0.12059), normal=(0.0, 1.0, 0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.01482, 0.59369)
loop_1 = loop_1.lineTo(-1.01482, -0.26345)
loop_1 = loop_1.lineTo(-0.36938, -0.26345)
loop_1 = loop_1.lineTo(-0.36938, -0.83488)
loop_1 = loop_1.lineTo(0.48776, -0.83488)
loop_1 = loop_1.lineTo(0.48776, -0.26345)
loop_1 = loop_1.lineTo(0.98518, -0.26345)
loop_1 = loop_1.lineTo(0.98518, 0.59369)
loop_1 = loop_1.lineTo(-1.00649, 0.59369)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.86)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0031_00313534/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0031_00313534/sketch_1_interval_0.stl')