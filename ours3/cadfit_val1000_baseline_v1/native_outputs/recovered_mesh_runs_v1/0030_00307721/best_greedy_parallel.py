import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00204, -0.66338, -0.00416), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.77565, 0.99584)
loop_1 = loop_1.lineTo(0.77974, 0.99584)
loop_1 = loop_1.lineTo(0.77974, 0.55152)
loop_1 = loop_1.lineTo(0.33543, 0.55152)
loop_1 = loop_1.lineTo(0.33543, -0.55955)
loop_1 = loop_1.lineTo(0.77974, -0.55955)
loop_1 = loop_1.lineTo(0.77974, -1.00416)
loop_1 = loop_1.lineTo(-0.77565, -1.00416)
loop_1 = loop_1.lineTo(-0.77565, -0.55955)
loop_1 = loop_1.lineTo(-0.33134, -0.55955)
loop_1 = loop_1.lineTo(-0.33134, 0.55152)
loop_1 = loop_1.lineTo(-0.77565, 0.55152)
loop_1 = loop_1.lineTo(-0.77565, 0.97918)
loop_1 = loop_1.lineTo(-0.77565, 0.99584)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0030_00307721/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0030_00307721/sketch_1_interval_0.stl')