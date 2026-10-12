import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.61, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28, 0.84549)
loop_1 = loop_1.lineTo(-0.28, 0.84395)
loop_1 = loop_1.lineTo(-0.27847, 0.48745)
loop_1 = loop_1.lineTo(-0.25, 0.48745)
loop_1 = loop_1.lineTo(-0.25305, -0.48745)
loop_1 = loop_1.lineTo(-0.28, -0.48745)
loop_1 = loop_1.lineTo(-0.27845, -0.84549)
loop_1 = loop_1.lineTo(0.28, -0.84395)
loop_1 = loop_1.lineTo(0.27847, -0.48745)
loop_1 = loop_1.lineTo(0.25, -0.48745)
loop_1 = loop_1.lineTo(0.25305, 0.48745)
loop_1 = loop_1.lineTo(0.28, 0.48745)
loop_1 = loop_1.lineTo(0.28, 0.84395)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0089_00894171/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0089_00894171/sketch_12_interval_0.stl')