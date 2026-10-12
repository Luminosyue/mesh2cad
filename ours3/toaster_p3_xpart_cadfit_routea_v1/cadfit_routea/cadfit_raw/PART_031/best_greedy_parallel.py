import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.99, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00253, 0.00323)
loop_1 = loop_1.circle(0.03419)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.98)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw/PART_031/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/toaster_p3_xpart_cadfit_routea_v1/cadfit_routea/cadfit_raw/PART_031/sketch_24_interval_0.stl')