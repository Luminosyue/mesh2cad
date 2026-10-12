import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.66667, 0.66667)
loop_1 = loop_1.lineTo(-0.6635, -0.00328)
loop_1 = loop_1.lineTo(-0.01937, -0.66456)
loop_1 = loop_1.lineTo(0.66667, 0.00456)
loop_1 = loop_1.lineTo(0.66363, 0.66667)
loop_1 = loop_1.lineTo(-0.66515, 0.66667)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0031_00318585/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0031_00318585/sketch_1_interval_0.stl')