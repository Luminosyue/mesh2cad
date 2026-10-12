import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.62697), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.20488, -0.50128)
loop_1 = loop_1.lineTo(-0.02068, -0.57933)
loop_1 = loop_1.lineTo(-0.04401, -0.58531)
loop_1 = loop_1.lineTo(-0.05731, -0.58929)
loop_1 = loop_1.lineTo(-0.07714, -0.58816)
loop_1 = loop_1.lineTo(-0.0942, -0.58365)
loop_1 = loop_1.lineTo(-0.11204, -0.56992)
loop_1 = loop_1.lineTo(-0.22, -0.56958)
loop_1 = loop_1.lineTo(-0.21964, -0.48678)
loop_1 = loop_1.lineTo(-0.2079, -0.49862)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_94_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_94_interval_1.stl')