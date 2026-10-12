import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.21089, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15678, 0.04625)
loop_1 = loop_1.lineTo(0.1371, 0.04574)
loop_1 = loop_1.lineTo(0.11738, 0.03537)
loop_1 = loop_1.lineTo(0.09755, 0.01679)
loop_1 = loop_1.lineTo(0.08219, -0.00623)
loop_1 = loop_1.lineTo(0.0773, -0.02592)
loop_1 = loop_1.lineTo(0.07751, -0.04496)
loop_1 = loop_1.lineTo(0.08936, -0.06471)
loop_1 = loop_1.lineTo(0.11819, -0.07444)
loop_1 = loop_1.lineTo(0.13777, -0.06957)
loop_1 = loop_1.lineTo(0.15732, -0.05694)
loop_1 = loop_1.lineTo(0.17005, -0.04446)
loop_1 = loop_1.lineTo(0.1822, -0.02454)
loop_1 = loop_1.lineTo(0.19037, -0.00505)
loop_1 = loop_1.lineTo(0.19134, 0.01412)
loop_1 = loop_1.lineTo(0.18033, 0.03349)
loop_1 = loop_1.lineTo(0.15689, 0.04621)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/sketch_8_interval_0.stl')