import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.04401, -0.19486, 0.54959), normal=(-0.00136, -0.00047, -1.0), xDir=(0.0, -1.0, 0.00047))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0919, -0.9093)
loop_1 = loop_1.lineTo(-0.0753, -0.90779)
loop_1 = loop_1.threePointArc((-0.04985, -0.90513), (-0.02758, -0.90328))
loop_1 = loop_1.threePointArc((0.02789, -0.89489), (0.07607, -0.88515))
loop_1 = loop_1.lineTo(0.10093, -0.87797)
loop_1 = loop_1.lineTo(0.12791, -0.87221)
loop_1 = loop_1.lineTo(0.15281, -0.85992)
loop_1 = loop_1.lineTo(0.17975, -0.84973)
loop_1 = loop_1.lineTo(0.2047, -0.83829)
loop_1 = loop_1.lineTo(0.22716, -0.82972)
loop_1 = loop_1.lineTo(0.25373, -0.81867)
loop_1 = loop_1.lineTo(0.28464, -0.803)
loop_1 = loop_1.lineTo(0.28464, -0.91038)
loop_1 = loop_1.lineTo(-0.09945, -0.90994)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_18_interval_0.stl')