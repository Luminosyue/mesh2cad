import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.25), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29768, 0.89936)
loop_1 = loop_1.lineTo(-0.29346, -0.5913)
loop_1 = loop_1.threePointArc((-0.24365, -0.65424), (-0.19467, -0.71203))
loop_1 = loop_1.lineTo(-0.09355, -0.83336)
loop_1 = loop_1.threePointArc((-0.05332, -0.87793), (-0.01838, -0.92816))
loop_1 = loop_1.lineTo(-0.00807, -0.9128)
loop_1 = loop_1.lineTo(-0.05094, -0.85502)
loop_1 = loop_1.threePointArc((-0.13674, -0.7542), (-0.22241, -0.648))
loop_1 = loop_1.threePointArc((-0.25054, -0.61495), (-0.27639, -0.57963))
loop_1 = loop_1.threePointArc((-0.27886, -0.5691), (-0.27806, -0.55943))
loop_1 = loop_1.threePointArc((-0.27768, 0.18275), (-0.2788, 0.89394))
loop_1 = loop_1.lineTo(-0.25899, 0.90426)
loop_1 = loop_1.threePointArc((-0.26181, 0.91467), (-0.26616, 0.91742))
loop_1 = loop_1.threePointArc((-0.28148, 0.91433), (-0.29477, 0.91143))
loop_1 = loop_1.lineTo(-0.29768, 0.89936)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.51)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/greedy_greedy_step_extrude.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/greedy_greedy_step_extrude.stl')