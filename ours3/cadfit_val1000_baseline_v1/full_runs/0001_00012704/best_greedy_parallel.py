import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.33215, 0.15322, -0.89635), normal=(0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.94687, 0.66785)
loop_1 = loop_1.lineTo(-0.94687, -0.91945)
loop_1 = loop_1.lineTo(0.64043, -0.91945)
loop_1 = loop_1.lineTo(0.64043, 0.66785)
loop_1 = loop_1.lineTo(-0.91543, 0.66785)
loop_1 = loop_1.lineTo(-0.94687, 0.66785)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.69)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/full_runs/0001_00012704/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/full_runs/0001_00012704/sketch_0_interval_0.stl')