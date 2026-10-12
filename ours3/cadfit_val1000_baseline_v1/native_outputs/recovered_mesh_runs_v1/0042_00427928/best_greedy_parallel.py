import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.33666, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.59042)
loop_1 = loop_1.lineTo(0.99788, 0.25708)
loop_1 = loop_1.lineTo(0.33332, 0.25496)
loop_1 = loop_1.lineTo(0.3312, -0.58301)
loop_1 = loop_1.lineTo(-0.33332, -0.5883)
loop_1 = loop_1.lineTo(-0.33544, 0.25708)
loop_1 = loop_1.lineTo(-1.0, 0.2592)
loop_1 = loop_1.lineTo(-0.99788, 0.59042)
loop_1 = loop_1.lineTo(0.99788, 0.59042)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.67)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0042_00427928/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0042_00427928/sketch_11_interval_0.stl')