import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.20751, -0.04743, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.55257, 1.20751)
loop_1 = loop_1.lineTo(-0.55257, -0.79249)
loop_1 = loop_1.lineTo(0.64743, -0.79249)
loop_1 = loop_1.lineTo(0.64743, 1.20751)
loop_1 = loop_1.lineTo(-0.52095, 1.20751)
loop_1 = loop_1.lineTo(-0.55257, 1.20751)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.35257, 1.00751)
loop_2 = loop_2.lineTo(0.44743, 1.00751)
loop_2 = loop_2.lineTo(0.44743, -0.59249)
loop_2 = loop_2.lineTo(-0.35257, -0.59249)
loop_2 = loop_2.lineTo(-0.35257, 0.98751)
loop_2 = loop_2.lineTo(-0.35257, 1.00751)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__104453_aba0f2d1_0006/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__104453_aba0f2d1_0006/sketch_1_interval_0.stl')