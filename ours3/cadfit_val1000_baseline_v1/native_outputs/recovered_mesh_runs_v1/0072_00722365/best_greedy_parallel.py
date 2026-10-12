import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.19079, -0.00046, -0.28028), normal=(0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.24662, 0.80921)
loop_1 = loop_1.lineTo(-0.24495, -0.52412)
loop_1 = loop_1.lineTo(-0.1394, -0.52412)
loop_1 = loop_1.lineTo(-0.13782, -1.08477)
loop_1 = loop_1.lineTo(0.00046, -1.19079)
loop_1 = loop_1.lineTo(0.00324, -0.52412)
loop_1 = loop_1.lineTo(0.24755, -0.52412)
loop_1 = loop_1.lineTo(0.24755, 0.80921)
loop_1 = loop_1.lineTo(-0.24446, 0.80921)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.56)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0072_00722365/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0072_00722365/sketch_3_interval_0.stl')