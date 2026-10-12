import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.90609, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.5105, 0.20468)
loop_1 = loop_1.threePointArc((0.42056, 0.20493), (0.32688, 0.20571))
loop_1 = loop_1.lineTo(0.18363, 0.20771)
loop_1 = loop_1.threePointArc((0.13213, 0.20841), (0.08311, 0.20822))
loop_1 = loop_1.lineTo(0.03805, 0.20999)
loop_1 = loop_1.lineTo(0.02382, 0.21129)
loop_1 = loop_1.lineTo(0.28394, 0.20885)
loop_1 = loop_1.lineTo(0.1786, 0.21134)
loop_1 = loop_1.lineTo(0.55731, 0.21044)
loop_1 = loop_1.lineTo(0.54323, 0.20539)
loop_1 = loop_1.lineTo(0.51057, 0.2051)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_51_interval_0.stl')