import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.66667, 0.83333)
loop_1 = loop_1.lineTo(-0.66658, 0.82891)
loop_1 = loop_1.lineTo(-0.62794, -0.83333)
loop_1 = loop_1.lineTo(-0.29903, -0.83113)
loop_1 = loop_1.lineTo(-0.29682, -0.5)
loop_1 = loop_1.lineTo(0.36764, -0.50221)
loop_1 = loop_1.lineTo(0.36986, -0.83333)
loop_1 = loop_1.lineTo(0.66667, -0.83112)
loop_1 = loop_1.lineTo(0.66667, 0.83112)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0060_00607305/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0060_00607305/sketch_8_interval_0.stl')