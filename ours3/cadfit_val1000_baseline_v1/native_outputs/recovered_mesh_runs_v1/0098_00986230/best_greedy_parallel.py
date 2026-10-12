import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.23366, -0.11736, -0.2921), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.50984, 1.23366)
loop_1 = loop_1.lineTo(-0.50984, -0.76634)
loop_1 = loop_1.lineTo(0.74456, -0.76634)
loop_1 = loop_1.lineTo(0.74456, 1.23366)
loop_1 = loop_1.lineTo(-0.47712, 1.23366)
loop_1 = loop_1.lineTo(-0.50984, 1.23366)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.44184, 1.16565)
loop_2 = loop_2.lineTo(0.67655, 1.16565)
loop_2 = loop_2.lineTo(0.67655, -0.69834)
loop_2 = loop_2.lineTo(-0.44184, -0.69834)
loop_2 = loop_2.lineTo(-0.44184, 1.13328)
loop_2 = loop_2.lineTo(-0.44184, 1.16565)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.58)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0098_00986230/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0098_00986230/sketch_1_interval_0.stl')