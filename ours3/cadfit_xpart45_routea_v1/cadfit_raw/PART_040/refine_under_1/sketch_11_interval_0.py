import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35409, -0.82297)
loop_1 = loop_1.threePointArc((-0.35284, -0.83175), (-0.35153, -0.84016))
loop_1 = loop_1.lineTo(-0.3382, -0.85687)
loop_1 = loop_1.lineTo(-0.3281, -0.86252)
loop_1 = loop_1.threePointArc((-0.32066, -0.86439), (-0.31297, -0.86654))
loop_1 = loop_1.threePointArc((-0.30374, -0.86653), (-0.29633, -0.86653))
loop_1 = loop_1.threePointArc((-0.28742, -0.86452), (-0.27969, -0.86287))
loop_1 = loop_1.threePointArc((-0.27332, -0.85928), (-0.268, -0.85631))
loop_1 = loop_1.lineTo(-0.25536, -0.83809)
loop_1 = loop_1.threePointArc((-0.25449, -0.83067), (-0.25333, -0.82297))
loop_1 = loop_1.lineTo(-0.26724, -0.78701)
loop_1 = loop_1.threePointArc((-0.27359, -0.78332), (-0.27969, -0.77978))
loop_1 = loop_1.lineTo(-0.2968, -0.77523)
loop_1 = loop_1.threePointArc((-0.30517, -0.77473), (-0.31322, -0.77445))
loop_1 = loop_1.lineTo(-0.33064, -0.7801)
loop_1 = loop_1.threePointArc((-0.33803, -0.78488), (-0.34585, -0.78967))
loop_1 = loop_1.lineTo(-0.35409, -0.82297)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_11_interval_0.stl')