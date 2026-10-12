import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.59386, 0.11386, -0.05298), normal=(0.99863, 0.05217, 0.00296), xDir=(0.05217, -0.99864, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04261, 0.25703)
loop_1 = loop_1.lineTo(-0.05521, 0.25483)
loop_1 = loop_1.lineTo(-0.06988, 0.24174)
loop_1 = loop_1.lineTo(-0.07561, 0.2295)
loop_1 = loop_1.lineTo(-0.0739, 0.20806)
loop_1 = loop_1.lineTo(-0.05328, 0.18276)
loop_1 = loop_1.lineTo(-0.04152, 0.18461)
loop_1 = loop_1.lineTo(-0.02797, 0.19395)
loop_1 = loop_1.lineTo(-0.02204, 0.20411)
loop_1 = loop_1.lineTo(-0.01959, 0.21739)
loop_1 = loop_1.lineTo(-0.02018, 0.23092)
loop_1 = loop_1.lineTo(-0.02416, 0.24256)
loop_1 = loop_1.lineTo(-0.04196, 0.25658)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_27_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_27_interval_1.stl')