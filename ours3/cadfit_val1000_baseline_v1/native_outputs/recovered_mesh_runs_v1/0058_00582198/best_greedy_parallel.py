import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.41223, 0.51125, -0.41095), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.51277, 0.58905)
loop_1 = loop_1.lineTo(-1.41223, 0.58905)
loop_1 = loop_1.lineTo(-1.41223, 0.39155)
loop_1 = loop_1.lineTo(0.39027, 0.39155)
loop_1 = loop_1.lineTo(0.39027, -1.41095)
loop_1 = loop_1.lineTo(0.58777, -1.41095)
loop_1 = loop_1.lineTo(0.58777, 0.51405)
loop_1 = loop_1.lineTo(0.53654, 0.56528)
loop_1 = loop_1.lineTo(0.51277, 0.58905)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0058_00582198/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0058_00582198/sketch_0_interval_0.stl')