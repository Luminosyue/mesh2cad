import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01613, 0.6, -0.15192), normal=(0.0, -1.0, -0.0), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.01613, 0.44808)
loop_1 = loop_1.lineTo(-0.98387, 0.44808)
loop_1 = loop_1.lineTo(-0.98387, 0.04808)
loop_1 = loop_1.lineTo(-0.58387, 0.04808)
loop_1 = loop_1.lineTo(-0.58387, -0.75192)
loop_1 = loop_1.lineTo(-0.22387, -0.75192)
loop_1 = loop_1.lineTo(-0.22387, -0.27192)
loop_1 = loop_1.lineTo(0.25613, -0.27192)
loop_1 = loop_1.lineTo(0.25613, -0.75192)
loop_1 = loop_1.lineTo(0.61613, -0.75192)
loop_1 = loop_1.lineTo(0.61613, 0.04808)
loop_1 = loop_1.lineTo(1.01613, 0.04808)
loop_1 = loop_1.lineTo(1.01613, 0.40975)
loop_1 = loop_1.lineTo(1.01613, 0.44808)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0025_00255754/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0025_00255754/sketch_0_interval_0.stl')