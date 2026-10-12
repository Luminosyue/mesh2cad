import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.54335, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.80841, 0.04944)
loop_1 = loop_1.lineTo(-0.82944, 0.04883)
loop_1 = loop_1.lineTo(-0.82905, -0.30074)
loop_1 = loop_1.threePointArc((-0.82844, -0.26882), (-0.82844, -0.23843))
loop_1 = loop_1.lineTo(-0.82743, -0.20707)
loop_1 = loop_1.lineTo(-0.82862, -0.15549)
loop_1 = loop_1.threePointArc((-0.82706, -0.1312), (-0.82488, -0.10622))
loop_1 = loop_1.lineTo(-0.81153, -0.09018)
loop_1 = loop_1.lineTo(-0.80323, 0.03158)
loop_1 = loop_1.lineTo(-0.80833, 0.04918)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_55_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_55_interval_0.stl')