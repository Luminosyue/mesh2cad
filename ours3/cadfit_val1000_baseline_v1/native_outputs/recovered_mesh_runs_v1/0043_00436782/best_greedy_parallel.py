import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.32294), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.67674, 1.0)
loop_1 = loop_1.lineTo(-0.67372, -0.72702)
loop_1 = loop_1.lineTo(-0.35597, -0.72702)
loop_1 = loop_1.lineTo(-0.35379, -0.00649)
loop_1 = loop_1.lineTo(0.67674, -0.99393)
loop_1 = loop_1.lineTo(0.67371, 1.0)
loop_1 = loop_1.lineTo(0.34361, 1.0)
loop_1 = loop_1.lineTo(0.34152, -0.07998)
loop_1 = loop_1.lineTo(-0.67466, 0.99779)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.65)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0043_00436782/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0043_00436782/sketch_10_interval_0.stl')