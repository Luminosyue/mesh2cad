import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00107, 0.16857, 0.05363), normal=(0.0, -1.0, -0.0), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.99893, 0.65363)
loop_1 = loop_1.lineTo(0.99893, -0.54637)
loop_1 = loop_1.lineTo(-1.00107, -0.54637)
loop_1 = loop_1.lineTo(-1.00107, 0.65363)
loop_1 = loop_1.lineTo(0.96653, 0.65363)
loop_1 = loop_1.lineTo(0.99893, 0.65363)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.96465, 0.63077)
loop_2 = loop_2.lineTo(-0.96107, 0.63077)
loop_2 = loop_2.lineTo(-0.96107, -0.51209)
loop_2 = loop_2.lineTo(0.96465, -0.51209)
loop_2 = loop_2.lineTo(0.96465, 0.60026)
loop_2 = loop_2.lineTo(0.96465, 0.63077)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.34)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0006_00062678/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0006_00062678/sketch_3_interval_0.stl')