import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.1761, -0.2412, 1.12061), normal=(-0.0, -0.86736, 0.49768), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.33886, 1.35554)
loop_1 = loop_1.lineTo(-0.37456, 1.35498)
loop_1 = loop_1.lineTo(-0.24598, 1.35436)
loop_1 = loop_1.lineTo(-0.16809, 1.3541)
loop_1 = loop_1.threePointArc((-0.12445, 1.35383), (-0.08956, 1.35464))
loop_1 = loop_1.lineTo(0.13075, 1.35258)
loop_1 = loop_1.threePointArc((0.20407, 1.35297), (0.27278, 1.35226))
loop_1 = loop_1.threePointArc((0.30891, 1.35266), (0.33886, 1.35265))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_19_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_19_interval_1.stl')