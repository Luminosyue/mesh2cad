import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.52271), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.48, 0.99614)
loop_1 = loop_1.lineTo(-0.47948, 0.87429)
loop_1 = loop_1.threePointArc((-0.44656, 0.89168), (-0.41211, 0.90881))
loop_1 = loop_1.lineTo(-0.39622, 0.91661)
loop_1 = loop_1.lineTo(-0.34139, 0.93794)
loop_1 = loop_1.threePointArc((-0.31655, 0.94733), (-0.29078, 0.9565))
loop_1 = loop_1.threePointArc((-0.25948, 0.96541), (-0.22707, 0.9742))
loop_1 = loop_1.lineTo(-0.1846, 0.98458)
loop_1 = loop_1.lineTo(-0.1369, 0.99299)
loop_1 = loop_1.threePointArc((-0.12577, 0.99391), (-0.11541, 0.99527))
loop_1 = loop_1.lineTo(-0.4797, 0.99614)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_78_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_78_interval_0.stl')