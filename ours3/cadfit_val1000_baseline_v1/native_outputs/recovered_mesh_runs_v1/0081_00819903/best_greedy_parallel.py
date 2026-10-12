import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.13667), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.33333)
loop_1 = loop_1.lineTo(-0.99657, -0.33333)
loop_1 = loop_1.lineTo(1.0, -0.32819)
loop_1 = loop_1.lineTo(0.99714, 0.06857)
loop_1 = loop_1.lineTo(0.59485, 0.33333)
loop_1 = loop_1.lineTo(-0.99828, 0.33333)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.27)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0081_00819903/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0081_00819903/sketch_1_interval_0.stl')