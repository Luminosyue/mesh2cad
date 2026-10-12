import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.67583, 0.11897, -0.07256), normal=(-1.0, 0.0, 0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34631, -0.26142)
loop_1 = loop_1.lineTo(-0.20625, -0.26411)
loop_1 = loop_1.lineTo(-0.15937, -0.26988)
loop_1 = loop_1.lineTo(-0.11248, -0.28979)
loop_1 = loop_1.lineTo(-0.0656, -0.29618)
loop_1 = loop_1.lineTo(-0.03302, -0.29782)
loop_1 = loop_1.lineTo(0.08567, -0.30219)
loop_1 = loop_1.lineTo(0.35635, -0.30226)
loop_1 = loop_1.lineTo(0.39468, -0.30266)
loop_1 = loop_1.lineTo(0.44157, -0.30301)
loop_1 = loop_1.lineTo(0.47135, -0.30286)
loop_1 = loop_1.lineTo(0.5047, -0.29915)
loop_1 = loop_1.lineTo(0.52066, -0.29775)
loop_1 = loop_1.lineTo(0.54388, -0.27962)
loop_1 = loop_1.lineTo(0.5653, -0.26153)
loop_1 = loop_1.lineTo(-0.34412, -0.26142)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_15_interval_0.stl')