import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31322, 0.18001)
loop_1 = loop_1.lineTo(-0.31125, -0.18197)
loop_1 = loop_1.lineTo(0.00197, -0.36053)
loop_1 = loop_1.lineTo(0.31321, -0.17856)
loop_1 = loop_1.lineTo(0.31125, 0.18197)
loop_1 = loop_1.lineTo(-0.00197, 0.36053)
loop_1 = loop_1.lineTo(-0.31259, 0.18037)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.21875, 0.0)
loop_2 = loop_2.circle(0.07793)
loop_3 = sketch_1.moveTo(0.0, 0.0)
loop_3 = loop_3.circle(0.03117)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3)
solid_1 = sketch_1.extrude(2.01)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__65532_72eb1a5e_0004/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__65532_72eb1a5e_0004/sketch_31_interval_0.stl')