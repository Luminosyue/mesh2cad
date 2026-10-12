import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.07932, -0.37086, -0.06299), normal=(-0.99386, 0.07588, 0.0805), xDir=(0.07612, 0.9971, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17553, 0.04002)
loop_1 = loop_1.lineTo(-0.07048, 0.04002)
loop_1 = loop_1.lineTo(-0.05589, 0.04002)
loop_1 = loop_1.lineTo(0.36961, 0.04002)
loop_1 = loop_1.lineTo(0.35815, 0.05369)
loop_1 = loop_1.lineTo(0.34795, 0.05719)
loop_1 = loop_1.lineTo(0.33176, 0.06008)
loop_1 = loop_1.lineTo(0.27278, 0.06008)
loop_1 = loop_1.lineTo(0.2412, 0.06008)
loop_1 = loop_1.lineTo(-0.13907, 0.06008)
loop_1 = loop_1.lineTo(-0.16468, 0.06005)
loop_1 = loop_1.lineTo(-0.17553, 0.04002)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_10_interval_0.stl')