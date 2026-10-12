import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.58003, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.94609, 0.33246)
loop_1 = loop_1.lineTo(0.94837, 0.27996)
loop_1 = loop_1.lineTo(0.91118, 0.29638)
loop_1 = loop_1.lineTo(0.86905, 0.30179)
loop_1 = loop_1.threePointArc((0.86189, 0.30294), (0.85542, 0.30293))
loop_1 = loop_1.lineTo(0.80015, 0.30477)
loop_1 = loop_1.threePointArc((0.75518, 0.30521), (0.7125, 0.305))
loop_1 = loop_1.threePointArc((0.69003, 0.30371), (0.66897, 0.30218))
loop_1 = loop_1.threePointArc((0.64467, 0.29803), (0.6198, 0.2945))
loop_1 = loop_1.threePointArc((0.59721, 0.29282), (0.57419, 0.29157))
loop_1 = loop_1.threePointArc((0.54679, 0.29302), (0.52096, 0.29374))
loop_1 = loop_1.lineTo(0.37043, 0.29213)
loop_1 = loop_1.threePointArc((0.33314, 0.29184), (0.29485, 0.29307))
loop_1 = loop_1.lineTo(0.22209, 0.29276)
loop_1 = loop_1.lineTo(0.94558, 0.33243)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_30_interval_0.stl')