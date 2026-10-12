import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.22573, -0.06266, 0.01644), normal=(0.86268, -0.50576, -0.00026), xDir=(-0.50576, -0.86268, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01571, -0.50086)
loop_1 = loop_1.lineTo(-0.01592, -0.77467)
loop_1 = loop_1.lineTo(-0.02203, -0.76128)
loop_1 = loop_1.lineTo(-0.04774, -0.73289)
loop_1 = loop_1.lineTo(-0.0462, -0.72145)
loop_1 = loop_1.lineTo(-0.04452, -0.70202)
loop_1 = loop_1.lineTo(-0.03829, -0.68604)
loop_1 = loop_1.lineTo(-0.03642, -0.67592)
loop_1 = loop_1.lineTo(-0.03014, -0.65617)
loop_1 = loop_1.lineTo(-0.0346, -0.62872)
loop_1 = loop_1.threePointArc((-0.03506, -0.61291), (-0.03555, -0.60028))
loop_1 = loop_1.lineTo(-0.03463, -0.57966)
loop_1 = loop_1.lineTo(-0.03006, -0.56339)
loop_1 = loop_1.lineTo(-0.02728, -0.55139)
loop_1 = loop_1.threePointArc((-0.02369, -0.53979), (-0.02027, -0.52865))
loop_1 = loop_1.lineTo(-0.01765, -0.5148)
loop_1 = loop_1.lineTo(-0.01591, -0.50214)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_8_interval_0.stl')