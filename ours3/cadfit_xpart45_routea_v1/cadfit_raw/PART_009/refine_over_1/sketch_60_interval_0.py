import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.50396, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.87265, 0.14379)
loop_1 = loop_1.lineTo(-0.86005, 0.10061)
loop_1 = loop_1.lineTo(-0.83447, 0.05466)
loop_1 = loop_1.lineTo(-0.77825, -0.00263)
loop_1 = loop_1.lineTo(-0.7844, -0.02317)
loop_1 = loop_1.lineTo(-0.80162, -0.05456)
loop_1 = loop_1.lineTo(-0.83292, -0.06519)
loop_1 = loop_1.lineTo(-0.87082, -0.10664)
loop_1 = loop_1.lineTo(-0.87265, -0.13683)
loop_1 = loop_1.lineTo(-0.87265, 0.14358)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_60_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_60_interval_0.stl')