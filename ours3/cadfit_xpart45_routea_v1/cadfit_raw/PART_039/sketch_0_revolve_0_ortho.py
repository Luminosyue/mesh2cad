import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.5, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.20338, -0.00233)
sketch_1 = sketch_1.threePointArc((0.20344, -0.0134), (0.20328, -0.02492))
sketch_1 = sketch_1.threePointArc((0.20278, -0.03826), (0.20204, -0.05198))
sketch_1 = sketch_1.threePointArc((0.20126, -0.06272), (0.20121, -0.06501))
sketch_1 = sketch_1.lineTo(0.2011, -0.07512)
sketch_1 = sketch_1.threePointArc((0.19775, -0.08284), (0.19529, -0.08631))
sketch_1 = sketch_1.lineTo(0.1691, -0.0932)
sketch_1 = sketch_1.lineTo(0.15631, -0.09227)
sketch_1 = sketch_1.threePointArc((0.14611, -0.08102), (0.14479, -0.07755))
sketch_1 = sketch_1.threePointArc((0.14497, -0.06467), (0.14545, -0.06092))
sketch_1 = sketch_1.threePointArc((0.14586, -0.04483), (0.14584, -0.0381))
sketch_1 = sketch_1.lineTo(0.12568, -0.01426)
sketch_1 = sketch_1.threePointArc((0.12035, -0.00481), (0.11978, -0.00233))
sketch_1 = sketch_1.lineTo(0.20338, -0.00233)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.171, -0.001, -0.499), axisEnd=(-0.829, 0.008, -0.499))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_0_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_0_revolve_0_ortho.stl')