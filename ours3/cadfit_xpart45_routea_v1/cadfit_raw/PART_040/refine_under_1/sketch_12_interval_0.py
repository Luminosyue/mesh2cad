import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34296, -0.40839)
loop_1 = loop_1.threePointArc((-0.33927, -0.41467), (-0.33566, -0.42134))
loop_1 = loop_1.lineTo(-0.31932, -0.43505)
loop_1 = loop_1.lineTo(-0.29488, -0.44141)
loop_1 = loop_1.lineTo(-0.28328, -0.44031)
loop_1 = loop_1.lineTo(-0.26198, -0.43063)
loop_1 = loop_1.threePointArc((-0.25035, -0.41486), (-0.2463, -0.40711))
loop_1 = loop_1.threePointArc((-0.24604, -0.39812), (-0.24574, -0.3904))
loop_1 = loop_1.lineTo(-0.25214, -0.37275)
loop_1 = loop_1.lineTo(-0.28086, -0.35323)
loop_1 = loop_1.threePointArc((-0.28844, -0.35283), (-0.29633, -0.35232))
loop_1 = loop_1.threePointArc((-0.30508, -0.35364), (-0.31277, -0.35472))
loop_1 = loop_1.lineTo(-0.3296, -0.36433)
loop_1 = loop_1.lineTo(-0.33875, -0.37506)
loop_1 = loop_1.threePointArc((-0.34144, -0.3821), (-0.34396, -0.38889))
loop_1 = loop_1.lineTo(-0.34296, -0.40839)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_12_interval_0.stl')