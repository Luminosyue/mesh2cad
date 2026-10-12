import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31078, -0.28135)
loop_1 = loop_1.lineTo(-0.2949, -0.29426)
loop_1 = loop_1.threePointArc((-0.28714, -0.29638), (-0.27969, -0.29837))
loop_1 = loop_1.threePointArc((-0.27077, -0.29865), (-0.26305, -0.29895))
loop_1 = loop_1.lineTo(-0.22792, -0.28413)
loop_1 = loop_1.threePointArc((-0.22378, -0.27914), (-0.2194, -0.274))
loop_1 = loop_1.lineTo(-0.21357, -0.2579)
loop_1 = loop_1.lineTo(-0.21545, -0.24595)
loop_1 = loop_1.lineTo(-0.23201, -0.22153)
loop_1 = loop_1.threePointArc((-0.23933, -0.2183), (-0.24642, -0.21535))
loop_1 = loop_1.threePointArc((-0.25563, -0.21358), (-0.26305, -0.21233))
loop_1 = loop_1.threePointArc((-0.27197, -0.21304), (-0.27969, -0.21346))
loop_1 = loop_1.threePointArc((-0.28853, -0.21625), (-0.29555, -0.21847))
loop_1 = loop_1.lineTo(-0.30548, -0.27792)
loop_1 = loop_1.lineTo(-0.3157, -0.27436)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_13_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_13_interval_0.stl')