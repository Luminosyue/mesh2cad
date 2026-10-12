import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.24284, 0.00202, 0.91092), normal=(-0.13998, -0.00471, -0.99014), xDir=(0.0, -0.99999, 0.00476))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.78615, -0.17421)
loop_1 = loop_1.lineTo(-0.78728, -0.15579)
loop_1 = loop_1.threePointArc((-0.79482, -0.12464), (-0.80119, -0.09989))
loop_1 = loop_1.lineTo(-0.8012, -0.06186)
loop_1 = loop_1.lineTo(-0.79889, -0.03327)
loop_1 = loop_1.lineTo(-0.80699, 0.00044)
loop_1 = loop_1.lineTo(-0.80553, 0.02134)
loop_1 = loop_1.lineTo(-0.80725, 0.06274)
loop_1 = loop_1.lineTo(-0.80665, 0.07593)
loop_1 = loop_1.lineTo(-0.80737, 0.13606)
loop_1 = loop_1.lineTo(-0.80872, 0.16932)
loop_1 = loop_1.lineTo(-0.80751, 0.18441)
loop_1 = loop_1.lineTo(-0.80456, 0.25464)
loop_1 = loop_1.lineTo(-0.79898, 0.31858)
loop_1 = loop_1.lineTo(-0.7956, 0.3488)
loop_1 = loop_1.threePointArc((-0.79006, 0.37933), (-0.78618, 0.40258))
loop_1 = loop_1.lineTo(-0.78615, -0.16882)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.88)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_30_interval_0.stl')