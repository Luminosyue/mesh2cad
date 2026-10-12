import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00843, -0.34986, -0.0954), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.03584, -0.43169)
loop_1 = loop_1.lineTo(-1.07258, -0.42551)
loop_1 = loop_1.lineTo(-1.10551, -0.40921)
loop_1 = loop_1.lineTo(-1.12368, -0.40154)
loop_1 = loop_1.lineTo(-1.16601, -0.3899)
loop_1 = loop_1.lineTo(-1.21491, -0.38039)
loop_1 = loop_1.lineTo(-1.26382, -0.3732)
loop_1 = loop_1.lineTo(-1.28536, -0.37634)
loop_1 = loop_1.lineTo(-1.2617, -0.37111)
loop_1 = loop_1.lineTo(-1.20954, -0.37855)
loop_1 = loop_1.lineTo(-1.1608, -0.38745)
loop_1 = loop_1.lineTo(-1.11464, -0.39766)
loop_1 = loop_1.lineTo(-1.08517, -0.40893)
loop_1 = loop_1.lineTo(-1.05814, -0.4207)
loop_1 = loop_1.lineTo(-1.03818, -0.43054)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_22_interval_0.stl')