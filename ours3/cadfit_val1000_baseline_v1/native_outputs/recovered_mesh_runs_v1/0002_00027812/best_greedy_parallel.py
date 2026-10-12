import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.75, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 1.0)
loop_1 = loop_1.lineTo(1.0, 0.99535)
loop_1 = loop_1.lineTo(0.99537, -1.0)
loop_1 = loop_1.lineTo(0.74836, -0.99836)
loop_1 = loop_1.lineTo(-1.0, 0.75926)
loop_1 = loop_1.lineTo(-1.0, 0.99769)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0002_00027812/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0002_00027812/sketch_0_interval_0.stl')