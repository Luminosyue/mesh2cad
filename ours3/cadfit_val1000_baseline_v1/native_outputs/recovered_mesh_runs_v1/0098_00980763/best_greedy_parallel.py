import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00245, 0.125, -0.00419), normal=(0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.24755, 0.99581)
loop_1 = loop_1.lineTo(-0.25245, 0.99581)
loop_1 = loop_1.lineTo(-0.25245, 0.49581)
loop_1 = loop_1.lineTo(-0.54169, 0.49581)
loop_1 = loop_1.lineTo(-0.54169, -0.50419)
loop_1 = loop_1.lineTo(-0.25245, -0.50419)
loop_1 = loop_1.lineTo(-0.25245, -1.00419)
loop_1 = loop_1.lineTo(0.24755, -1.00419)
loop_1 = loop_1.lineTo(0.24755, -0.50419)
loop_1 = loop_1.lineTo(0.53679, -0.50419)
loop_1 = loop_1.lineTo(0.53679, 0.49581)
loop_1 = loop_1.lineTo(0.24755, 0.49581)
loop_1 = loop_1.lineTo(0.24755, 0.96504)
loop_1 = loop_1.lineTo(0.24755, 0.99581)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0098_00980763/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0098_00980763/sketch_0_interval_0.stl')