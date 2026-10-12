import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05794, -0.63812, -0.05583), normal=(-0.00029, -0.99999, -0.0052), xDir=(-1.0, 0.00029, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35118, 0.13036)
loop_1 = loop_1.lineTo(-0.3542, -0.13522)
loop_1 = loop_1.lineTo(-0.35647, -0.10022)
loop_1 = loop_1.lineTo(-0.35721, -0.08928)
loop_1 = loop_1.threePointArc((-0.3577, -0.06598), (-0.35836, -0.0461))
loop_1 = loop_1.threePointArc((-0.3574, -0.00746), (-0.35722, 0.02715))
loop_1 = loop_1.threePointArc((-0.35676, 0.05605), (-0.35603, 0.08342))
loop_1 = loop_1.threePointArc((-0.35412, 0.10678), (-0.35259, 0.1266))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_7_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_7_interval_1.stl')