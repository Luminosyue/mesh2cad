import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.60471, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.83395, -0.24973)
loop_1 = loop_1.threePointArc((-0.83318, -0.27663), (-0.83213, -0.30243))
loop_1 = loop_1.threePointArc((-0.83208, -0.31891), (-0.8314, -0.33453))
loop_1 = loop_1.threePointArc((-0.83052, -0.35774), (-0.82925, -0.37981))
loop_1 = loop_1.threePointArc((-0.82819, -0.40227), (-0.82736, -0.42548))
loop_1 = loop_1.lineTo(-0.82519, -0.47258)
loop_1 = loop_1.lineTo(-0.81964, -0.5171)
loop_1 = loop_1.lineTo(-0.81438, -0.53018)
loop_1 = loop_1.lineTo(-0.83394, -0.52999)
loop_1 = loop_1.lineTo(-0.83394, -0.24993)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_85_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_85_interval_0.stl')