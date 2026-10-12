import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.35554, 0.20229)
loop_1 = loop_1.lineTo(0.42932, 0.19232)
loop_1 = loop_1.lineTo(0.44041, 0.21031)
loop_1 = loop_1.threePointArc((0.44109, 0.21736), (0.44182, 0.2247))
loop_1 = loop_1.lineTo(0.38483, 0.2758)
loop_1 = loop_1.threePointArc((0.37712, 0.27288), (0.36905, 0.26997))
loop_1 = loop_1.lineTo(0.35474, 0.25759)
loop_1 = loop_1.threePointArc((0.35062, 0.24963), (0.34671, 0.24197))
loop_1 = loop_1.threePointArc((0.34655, 0.23358), (0.3464, 0.22648))
loop_1 = loop_1.lineTo(0.35554, 0.20229)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_26_interval_0.stl')