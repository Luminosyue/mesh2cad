import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.3552, 0.34744, 0.01794), normal=(-0.86352, -0.50432, -0.00245), xDir=(-0.50432, 0.86352, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.74016, -0.15601)
loop_1 = loop_1.lineTo(-0.6202, -0.15603)
loop_1 = loop_1.lineTo(-0.62423, -0.16605)
loop_1 = loop_1.lineTo(-0.62631, -0.17985)
loop_1 = loop_1.threePointArc((-0.62813, -0.19165), (-0.62926, -0.19836))
loop_1 = loop_1.lineTo(-0.63696, -0.21429)
loop_1 = loop_1.lineTo(-0.64783, -0.22124)
loop_1 = loop_1.threePointArc((-0.65673, -0.22332), (-0.66524, -0.22545))
loop_1 = loop_1.lineTo(-0.6845, -0.226)
loop_1 = loop_1.threePointArc((-0.6949, -0.22561), (-0.70377, -0.22526))
loop_1 = loop_1.lineTo(-0.72304, -0.22049)
loop_1 = loop_1.lineTo(-0.73393, -0.21256)
loop_1 = loop_1.lineTo(-0.74173, -0.19662)
loop_1 = loop_1.lineTo(-0.74434, -0.18101)
loop_1 = loop_1.lineTo(-0.74944, -0.16687)
loop_1 = loop_1.lineTo(-0.74016, -0.15601)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_42_interval_0.stl')