import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00579, -0.07828, -0.50286), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.42172, 0.99421)
loop_1 = loop_1.lineTo(-0.42172, -1.00579)
loop_1 = loop_1.lineTo(0.43542, -1.00579)
loop_1 = loop_1.lineTo(0.43542, 0.99421)
loop_1 = loop_1.lineTo(-0.3929, 0.99421)
loop_1 = loop_1.lineTo(-0.42172, 0.99421)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.86)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0063_00638323/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0063_00638323/sketch_0_interval_0.stl')