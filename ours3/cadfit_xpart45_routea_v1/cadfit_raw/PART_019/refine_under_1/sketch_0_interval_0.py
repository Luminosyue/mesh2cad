import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.91965, 0.02545, -0.14912), normal=(-0.99919, 0.0005, 0.04016), xDir=(0.00051, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.80627, 0.33952)
loop_1 = loop_1.lineTo(-0.8136, 0.3241)
loop_1 = loop_1.threePointArc((-0.82046, 0.29241), (-0.82672, 0.26789))
loop_1 = loop_1.threePointArc((-0.82873, 0.23221), (-0.83062, 0.20359))
loop_1 = loop_1.threePointArc((-0.83034, 0.13665), (-0.83144, 0.07495))
loop_1 = loop_1.lineTo(-0.83046, 0.00294)
loop_1 = loop_1.threePointArc((-0.83064, -0.04409), (-0.83021, -0.08186))
loop_1 = loop_1.lineTo(-0.83283, -0.11801)
loop_1 = loop_1.lineTo(-0.83245, -0.1436)
loop_1 = loop_1.lineTo(-0.83561, -0.18233)
loop_1 = loop_1.lineTo(-0.83502, -0.20533)
loop_1 = loop_1.threePointArc((-0.83282, -0.23977), (-0.83181, -0.26707))
loop_1 = loop_1.lineTo(-0.82536, -0.31098)
loop_1 = loop_1.lineTo(-0.82514, -0.33703)
loop_1 = loop_1.lineTo(-0.81293, -0.39054)
loop_1 = loop_1.lineTo(-0.80717, -0.42148)
loop_1 = loop_1.lineTo(-0.80627, 0.33801)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.83)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_0_interval_0.stl')