import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.23028), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.87915, -0.46069)
loop_1 = loop_1.threePointArc((-0.88769, -0.44904), (-0.8961, -0.43656))
loop_1 = loop_1.threePointArc((-0.90417, -0.4245), (-0.91182, -0.41181))
loop_1 = loop_1.threePointArc((-0.9192, -0.39948), (-0.92612, -0.38657))
loop_1 = loop_1.threePointArc((-0.92997, -0.37953), (-0.93279, -0.37202))
loop_1 = loop_1.threePointArc((-0.94003, -0.35347), (-0.94707, -0.33432))
loop_1 = loop_1.lineTo(-0.96043, -0.29399)
loop_1 = loop_1.threePointArc((-0.96648, -0.27379), (-0.97239, -0.25296))
loop_1 = loop_1.threePointArc((-0.97783, -0.23111), (-0.98246, -0.20843))
loop_1 = loop_1.threePointArc((-0.98529, -0.19214), (-0.98767, -0.17539))
loop_1 = loop_1.threePointArc((-0.9892, -0.16178), (-0.99042, -0.14788))
loop_1 = loop_1.lineTo(-0.81406, -0.55095)
loop_1 = loop_1.threePointArc((-0.83836, -0.5145), (-0.86281, -0.48064))
loop_1 = loop_1.threePointArc((-0.87103, -0.46864), (-0.87902, -0.45616))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_52_interval_0.stl')