import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02156, -1.0, 0.00207), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02156, 0.66873)
loop_1 = loop_1.lineTo(0.27668, 0.61799)
loop_1 = loop_1.lineTo(0.49296, 0.47348)
loop_1 = loop_1.lineTo(0.63748, 0.25719)
loop_1 = loop_1.lineTo(0.68823, 0.00207)
loop_1 = loop_1.lineTo(0.63748, -0.25306)
loop_1 = loop_1.lineTo(0.49296, -0.46934)
loop_1 = loop_1.lineTo(0.27668, -0.61385)
loop_1 = loop_1.lineTo(0.02156, -0.6646)
loop_1 = loop_1.lineTo(-0.23356, -0.61385)
loop_1 = loop_1.lineTo(-0.44984, -0.46934)
loop_1 = loop_1.lineTo(-0.59436, -0.25306)
loop_1 = loop_1.lineTo(-0.64511, 0.00207)
loop_1 = loop_1.lineTo(-0.59436, 0.25719)
loop_1 = loop_1.lineTo(-0.44984, 0.47348)
loop_1 = loop_1.lineTo(-0.23356, 0.61799)
loop_1 = loop_1.lineTo(0.01518, 0.66746)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0078_00784578/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0078_00784578/sketch_1_interval_0.stl')