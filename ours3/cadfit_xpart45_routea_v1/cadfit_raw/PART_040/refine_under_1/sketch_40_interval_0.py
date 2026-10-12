import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.05307, 0.32162)
loop_1 = loop_1.threePointArc((0.04746, 0.31745), (0.04154, 0.31318))
loop_1 = loop_1.threePointArc((0.02759, 0.30464), (0.0197, 0.30073))
loop_1 = loop_1.lineTo(-0.02082, 0.30786)
loop_1 = loop_1.lineTo(-0.03256, 0.32393)
loop_1 = loop_1.threePointArc((-0.03384, 0.33134), (-0.03516, 0.33844))
loop_1 = loop_1.lineTo(-0.0263, 0.37286)
loop_1 = loop_1.lineTo(-0.01348, 0.38731)
loop_1 = loop_1.lineTo(0.00439, 0.39545)
loop_1 = loop_1.threePointArc((0.01195, 0.39648), (0.01985, 0.39738))
loop_1 = loop_1.lineTo(0.04037, 0.38986)
loop_1 = loop_1.lineTo(0.02851, 0.38572)
loop_1 = loop_1.lineTo(0.04885, 0.32758)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_40_interval_0.stl')