import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.39917, -0.71966)
loop_1 = loop_1.threePointArc((-0.3958, -0.72693), (-0.39247, -0.73458))
loop_1 = loop_1.threePointArc((-0.38349, -0.7432), (-0.37582, -0.75039))
loop_1 = loop_1.threePointArc((-0.3647, -0.75657), (-0.359, -0.75944))
loop_1 = loop_1.threePointArc((-0.35052, -0.76134), (-0.34246, -0.76302))
loop_1 = loop_1.threePointArc((-0.33379, -0.76114), (-0.32563, -0.75922))
loop_1 = loop_1.threePointArc((-0.31899, -0.75579), (-0.31277, -0.75245))
loop_1 = loop_1.lineTo(-0.29844, -0.73599)
loop_1 = loop_1.lineTo(-0.29424, -0.71924)
loop_1 = loop_1.lineTo(-0.29551, -0.70284)
loop_1 = loop_1.lineTo(-0.30572, -0.6861)
loop_1 = loop_1.threePointArc((-0.31803, -0.67698), (-0.32625, -0.6715))
loop_1 = loop_1.threePointArc((-0.33446, -0.66971), (-0.34282, -0.66766))
loop_1 = loop_1.lineTo(-0.35946, -0.67075)
loop_1 = loop_1.threePointArc((-0.36811, -0.67481), (-0.37637, -0.6788))
loop_1 = loop_1.lineTo(-0.39285, -0.69476)
loop_1 = loop_1.threePointArc((-0.39788, -0.70812), (-0.39836, -0.71321))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/greedy_greedy_step_extrude.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/greedy_greedy_step_extrude.stl')