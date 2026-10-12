import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.23), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.40008, -0.71965)
loop_1 = loop_1.lineTo(-0.39508, -0.73662)
loop_1 = loop_1.lineTo(-0.37876, -0.75321)
loop_1 = loop_1.lineTo(-0.35883, -0.76181)
loop_1 = loop_1.lineTo(-0.34235, -0.76413)
loop_1 = loop_1.lineTo(-0.32563, -0.76065)
loop_1 = loop_1.lineTo(-0.30934, -0.75276)
loop_1 = loop_1.lineTo(-0.29649, -0.73598)
loop_1 = loop_1.lineTo(-0.29308, -0.71923)
loop_1 = loop_1.lineTo(-0.29527, -0.70274)
loop_1 = loop_1.lineTo(-0.30565, -0.68612)
loop_1 = loop_1.lineTo(-0.32641, -0.67329)
loop_1 = loop_1.lineTo(-0.34316, -0.67034)
loop_1 = loop_1.lineTo(-0.35976, -0.67253)
loop_1 = loop_1.lineTo(-0.37644, -0.67981)
loop_1 = loop_1.lineTo(-0.39303, -0.6962)
loop_1 = loop_1.lineTo(-0.40006, -0.71955)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/sketch_25_interval_0.stl')