import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.40086, -0.33817, 0.12248), normal=(5e-05, -0.71751, 0.69654), xDir=(-1.0, -8e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.88307, -0.07873)
loop_1 = loop_1.threePointArc((-0.82858, -0.07998), (-0.77625, -0.08033))
loop_1 = loop_1.lineTo(-1.37087, -0.08048)
loop_1 = loop_1.lineTo(-1.37086, 0.03346)
loop_1 = loop_1.lineTo(-1.3429, -0.04942)
loop_1 = loop_1.lineTo(-1.35567, -0.04151)
loop_1 = loop_1.lineTo(-1.36294, -0.02932)
loop_1 = loop_1.lineTo(-1.36314, -0.05106)
loop_1 = loop_1.lineTo(-1.33592, -0.05106)
loop_1 = loop_1.lineTo(-1.32302, -0.05383)
loop_1 = loop_1.threePointArc((-1.29707, -0.05668), (-1.27204, -0.05791))
loop_1 = loop_1.lineTo(-1.20916, -0.06188)
loop_1 = loop_1.threePointArc((-1.12944, -0.0674), (-1.05682, -0.07127))
loop_1 = loop_1.threePointArc((-1.01187, -0.07367), (-0.97239, -0.07494))
loop_1 = loop_1.threePointArc((-0.9261, -0.07746), (-0.88487, -0.07868))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_11_interval_0.stl')