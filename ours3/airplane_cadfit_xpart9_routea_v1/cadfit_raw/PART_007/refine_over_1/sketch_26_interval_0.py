import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.88249, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.84421, -0.12307)
loop_1 = loop_1.lineTo(0.84088, -0.16644)
loop_1 = loop_1.lineTo(0.66505, -0.15743)
loop_1 = loop_1.threePointArc((0.67532, -0.15757), (0.68504, -0.15746))
loop_1 = loop_1.lineTo(0.71833, -0.15737)
loop_1 = loop_1.threePointArc((0.73751, -0.15738), (0.75733, -0.15756))
loop_1 = loop_1.lineTo(0.7786, -0.15644)
loop_1 = loop_1.lineTo(0.79875, -0.15401)
loop_1 = loop_1.lineTo(0.81972, -0.14548)
loop_1 = loop_1.threePointArc((0.83184, -0.1355), (0.83454, -0.13256))
loop_1 = loop_1.lineTo(0.84555, -0.117)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.3)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_26_interval_0.stl')