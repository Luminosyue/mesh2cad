import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0098, 1.0, 0.00381), normal=(0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0098, 0.67048)
loop_1 = loop_1.lineTo(0.24532, 0.61973)
loop_1 = loop_1.lineTo(0.4616, 0.47522)
loop_1 = loop_1.lineTo(0.60612, 0.25894)
loop_1 = loop_1.lineTo(0.65687, 0.00381)
loop_1 = loop_1.lineTo(0.60612, -0.25131)
loop_1 = loop_1.lineTo(0.4616, -0.4676)
loop_1 = loop_1.lineTo(0.24532, -0.61211)
loop_1 = loop_1.lineTo(-0.0098, -0.66285)
loop_1 = loop_1.lineTo(-0.26492, -0.61211)
loop_1 = loop_1.lineTo(-0.4812, -0.4676)
loop_1 = loop_1.lineTo(-0.62572, -0.25131)
loop_1 = loop_1.lineTo(-0.67647, 0.00381)
loop_1 = loop_1.lineTo(-0.62572, 0.25894)
loop_1 = loop_1.lineTo(-0.4812, 0.47522)
loop_1 = loop_1.lineTo(-0.26492, 0.61973)
loop_1 = loop_1.lineTo(-0.01617, 0.66921)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0081_00819353/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0081_00819353/sketch_0_interval_0.stl')