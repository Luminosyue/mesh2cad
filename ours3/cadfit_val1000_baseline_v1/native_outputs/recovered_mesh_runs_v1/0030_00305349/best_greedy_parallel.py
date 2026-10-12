import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.15648, -0.85978, -0.00272), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.42013, 0.5976)
loop_1 = loop_1.lineTo(0.55951, 0.5976)
loop_1 = loop_1.lineTo(0.69582, 0.56862)
loop_1 = loop_1.lineTo(0.82315, 0.51193)
loop_1 = loop_1.lineTo(0.93591, 0.43001)
loop_1 = loop_1.lineTo(1.02916, 0.32644)
loop_1 = loop_1.lineTo(1.09885, 0.20574)
loop_1 = loop_1.lineTo(1.14192, 0.0732)
loop_1 = loop_1.lineTo(1.15648, -0.06541)
loop_1 = loop_1.lineTo(0.48982, -0.06541)
loop_1 = loop_1.lineTo(0.48982, -0.60305)
loop_1 = loop_1.lineTo(-0.84352, -0.60305)
loop_1 = loop_1.lineTo(-0.84352, 0.47222)
loop_1 = loop_1.lineTo(0.10182, 0.47222)
loop_1 = loop_1.lineTo(0.15648, 0.51193)
loop_1 = loop_1.lineTo(0.28381, 0.56862)
loop_1 = loop_1.lineTo(0.41616, 0.59676)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.72)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0030_00305349/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0030_00305349/sketch_0_interval_0.stl')