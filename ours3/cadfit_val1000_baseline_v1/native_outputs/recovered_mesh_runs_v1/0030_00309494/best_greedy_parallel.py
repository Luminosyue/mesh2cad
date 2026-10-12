import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04759, -0.41333, -0.13968), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.95241, 0.19365)
loop_1 = loop_1.lineTo(-0.95241, -0.47301)
loop_1 = loop_1.lineTo(-0.74408, -0.47301)
loop_1 = loop_1.lineTo(-0.74408, -0.05635)
loop_1 = loop_1.lineTo(0.67259, -0.05635)
loop_1 = loop_1.lineTo(0.67259, -0.30635)
loop_1 = loop_1.lineTo(0.92259, -0.30635)
loop_1 = loop_1.lineTo(0.92259, -0.13968)
loop_1 = loop_1.lineTo(1.04759, -0.13968)
loop_1 = loop_1.lineTo(1.04759, 0.19365)
loop_1 = loop_1.lineTo(-0.92303, 0.19365)
loop_1 = loop_1.lineTo(-0.95241, 0.19365)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.83)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0030_00309494/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0030_00309494/sketch_0_interval_0.stl')