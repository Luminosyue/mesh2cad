import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.14907, 0.26848, 0.26019), normal=(-0.28014, -0.55463, -0.78353), xDir=(-0.8926, 0.45084, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14481, 0.29647)
loop_1 = loop_1.lineTo(-0.10924, 0.2759)
loop_1 = loop_1.lineTo(-0.0317, 0.22911)
loop_1 = loop_1.lineTo(-0.39327, 0.22911)
loop_1 = loop_1.lineTo(-0.3783, 0.24713)
loop_1 = loop_1.lineTo(-0.36721, 0.25722)
loop_1 = loop_1.lineTo(-0.35687, 0.26569)
loop_1 = loop_1.lineTo(-0.33859, 0.27867)
loop_1 = loop_1.lineTo(-0.27919, 0.29843)
loop_1 = loop_1.threePointArc((-0.23301, 0.30103), (-0.18881, 0.30536))
loop_1 = loop_1.lineTo(-0.14481, 0.29647)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_22_interval_0.stl')