import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.27, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28, -0.14)
loop_1 = loop_1.lineTo(0.25, -0.14144)
loop_1 = loop_1.lineTo(0.24952, -0.3)
loop_1 = loop_1.lineTo(-0.28, -0.29856)
loop_1 = loop_1.lineTo(-0.28, -0.14048)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.54)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0089_00894171/sketch_11_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0089_00894171/sketch_11_interval_1.stl')