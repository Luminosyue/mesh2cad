import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0205, 0.0205)
loop_1 = loop_1.lineTo(0.02032, -0.04707)
loop_1 = loop_1.lineTo(-0.04707, -0.04689)
loop_1 = loop_1.lineTo(-0.04689, 0.0205)
loop_1 = loop_1.lineTo(0.02041, 0.0205)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.01689, 0.01689)
loop_2 = loop_2.lineTo(-0.04347, 0.01673)
loop_2 = loop_2.lineTo(-0.04331, -0.04347)
loop_2 = loop_2.lineTo(0.01689, -0.04331)
loop_2 = loop_2.lineTo(0.01689, 0.01681)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0089_00890304/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0089_00890304/sketch_4_interval_0.stl')