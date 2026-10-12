import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.053, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02807, 0.65004)
loop_1 = loop_1.lineTo(-0.02848, 0.50061)
loop_1 = loop_1.lineTo(-0.0408, 0.50476)
loop_1 = loop_1.lineTo(-0.04992, 0.51565)
loop_1 = loop_1.lineTo(-0.04824, 0.52956)
loop_1 = loop_1.threePointArc((-0.04811, 0.53493), (-0.04775, 0.5404))
loop_1 = loop_1.threePointArc((-0.04739, 0.54702), (-0.04715, 0.55328))
loop_1 = loop_1.threePointArc((-0.04739, 0.56368), (-0.04769, 0.57355))
loop_1 = loop_1.lineTo(-0.04923, 0.59008)
loop_1 = loop_1.lineTo(-0.04828, 0.61006)
loop_1 = loop_1.threePointArc((-0.04633, 0.61698), (-0.04466, 0.62356))
loop_1 = loop_1.lineTo(-0.03582, 0.64241)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_38_interval_0.stl')