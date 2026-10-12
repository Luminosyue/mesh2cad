import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.11766, -0.32683, -0.53572), normal=(-0.00126, -0.97705, -0.213), xDir=(-1.0, 0.00129, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.27425, 0.2376)
loop_1 = loop_1.lineTo(-0.15003, 0.2376)
loop_1 = loop_1.threePointArc((-0.16125, 0.23011), (-0.17005, 0.22446))
loop_1 = loop_1.threePointArc((-0.18526, 0.19883), (-0.19483, 0.1812))
loop_1 = loop_1.lineTo(-0.20513, 0.1433)
loop_1 = loop_1.threePointArc((-0.20779, 0.12575), (-0.20953, 0.1118))
loop_1 = loop_1.lineTo(-0.20804, 0.06636)
loop_1 = loop_1.threePointArc((-0.20606, 0.04751), (-0.20435, 0.03244))
loop_1 = loop_1.lineTo(-0.19635, 0.00277)
loop_1 = loop_1.lineTo(-0.1927, -0.00824)
loop_1 = loop_1.lineTo(-0.18738, -0.02119)
loop_1 = loop_1.lineTo(-0.19667, -0.00559)
loop_1 = loop_1.lineTo(-0.20714, 0.01415)
loop_1 = loop_1.lineTo(-0.21914, 0.04744)
loop_1 = loop_1.threePointArc((-0.22533, 0.0659), (-0.23027, 0.08131))
loop_1 = loop_1.lineTo(-0.23909, 0.11027)
loop_1 = loop_1.lineTo(-0.27336, 0.23437)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_50_interval_0.stl')