import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43114, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28009, -0.36606)
loop_1 = loop_1.lineTo(-0.64997, -0.5176)
loop_1 = loop_1.lineTo(-0.34058, -0.36443)
loop_1 = loop_1.lineTo(-0.39494, -0.38649)
loop_1 = loop_1.lineTo(-0.44643, -0.41248)
loop_1 = loop_1.lineTo(-0.4984, -0.41709)
loop_1 = loop_1.lineTo(-0.55036, -0.4045)
loop_1 = loop_1.lineTo(-0.60161, -0.41917)
loop_1 = loop_1.lineTo(-0.63092, -0.47532)
loop_1 = loop_1.lineTo(-0.65517, -0.51616)
loop_1 = loop_1.threePointArc((-0.65976, -0.52224), (-0.66514, -0.52711))
loop_1 = loop_1.lineTo(-0.1463, -0.5216)
loop_1 = loop_1.lineTo(-0.18418, -0.46228)
loop_1 = loop_1.lineTo(-0.21325, -0.41743)
loop_1 = loop_1.lineTo(-0.23839, -0.38693)
loop_1 = loop_1.lineTo(-0.27894, -0.36639)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.84)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_46_interval_0.stl')