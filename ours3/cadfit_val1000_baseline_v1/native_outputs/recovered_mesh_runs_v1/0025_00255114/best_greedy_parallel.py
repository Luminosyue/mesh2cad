import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.5, 0.24863)
loop_1 = loop_1.lineTo(0.48775, 0.1406)
loop_1 = loop_1.lineTo(0.45506, 0.04229)
loop_1 = loop_1.lineTo(0.40164, -0.04845)
loop_1 = loop_1.lineTo(0.33179, -0.12496)
loop_1 = loop_1.lineTo(0.24609, -0.18613)
loop_1 = loop_1.lineTo(0.15116, -0.22761)
loop_1 = loop_1.lineTo(0.04798, -0.24863)
loop_1 = loop_1.lineTo(-0.05562, -0.24792)
loop_1 = loop_1.lineTo(-0.15842, -0.22515)
loop_1 = loop_1.lineTo(-0.25277, -0.18237)
loop_1 = loop_1.lineTo(-0.33743, -0.11976)
loop_1 = loop_1.lineTo(-0.40622, -0.04229)
loop_1 = loop_1.lineTo(-0.4581, 0.04934)
loop_1 = loop_1.lineTo(-0.48943, 0.14808)
loop_1 = loop_1.lineTo(-0.49914, 0.24863)
loop_1 = loop_1.lineTo(0.49914, 0.24863)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0025_00255114/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0025_00255114/sketch_4_interval_0.stl')