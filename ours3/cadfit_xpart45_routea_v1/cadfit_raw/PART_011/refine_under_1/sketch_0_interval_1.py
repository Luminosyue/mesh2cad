import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.35491, 0.12472, -0.01426), normal=(-0.89584, 0.44438, 0.00038), xDir=(0.44438, 0.89584, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.33804, 0.19403)
loop_1 = loop_1.lineTo(-0.35083, 0.17647)
loop_1 = loop_1.lineTo(-0.35544, 0.13353)
loop_1 = loop_1.lineTo(-0.35439, 0.08414)
loop_1 = loop_1.threePointArc((-0.35278, 0.04237), (-0.35043, 0.00604))
loop_1 = loop_1.threePointArc((-0.34892, -0.01613), (-0.34849, -0.03538))
loop_1 = loop_1.threePointArc((-0.34795, -0.05192), (-0.34739, -0.06406))
loop_1 = loop_1.threePointArc((-0.34801, -0.08951), (-0.3486, -0.11216))
loop_1 = loop_1.threePointArc((-0.34696, -0.13753), (-0.34589, -0.16027))
loop_1 = loop_1.lineTo(-0.33281, -0.17092)
loop_1 = loop_1.lineTo(-0.33319, 0.19652)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_0_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_0_interval_1.stl')