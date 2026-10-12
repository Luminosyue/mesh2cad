import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0379, -0.09133, -0.15871), normal=(-0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.55383, 0.9621)
loop_1 = loop_1.lineTo(-0.55383, -1.0379)
loop_1 = loop_1.lineTo(0.7365, -1.0379)
loop_1 = loop_1.lineTo(0.7365, 0.9621)
loop_1 = loop_1.lineTo(-0.52079, 0.9621)
loop_1 = loop_1.lineTo(-0.55383, 0.9621)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.47843, -0.81209)
loop_2 = loop_2.circle(0.09654)
loop_3 = sketch_1.moveTo(-0.29576, -0.81209)
loop_3 = loop_3.circle(0.09654)
loop_4 = sketch_1.moveTo(-0.29576, 0.7363)
loop_4 = loop_4.circle(0.09654)
loop_5 = sketch_1.moveTo(0.47843, 0.7363)
loop_5 = loop_5.circle(0.09654)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3).add(loop_4).add(loop_5)
solid_1 = sketch_1.extrude(0.32)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__84025_ec3401ea_0000/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__84025_ec3401ea_0000/sketch_1_interval_0.stl')