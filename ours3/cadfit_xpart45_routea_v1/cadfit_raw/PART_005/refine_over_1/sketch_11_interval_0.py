import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.77901, 0.52058, 0.13973), normal=(-0.78428, -0.62041, 7e-05), xDir=(-0.62041, 0.78428, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.34063, 0.65969)
loop_1 = loop_1.lineTo(0.36286, 0.65969)
loop_1 = loop_1.lineTo(0.36309, 0.45251)
loop_1 = loop_1.threePointArc((0.36341, 0.44141), (0.36358, 0.43265))
loop_1 = loop_1.lineTo(0.34536, 0.65321)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_11_interval_0.stl')