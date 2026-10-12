import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.63376, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.06349, 0.46266)
loop_1 = loop_1.lineTo(-0.04689, 0.46264)
loop_1 = loop_1.threePointArc((-0.04763, 0.44696), (-0.04979, 0.43128))
loop_1 = loop_1.lineTo(-0.05489, 0.39432)
loop_1 = loop_1.threePointArc((-0.05649, 0.37977), (-0.05871, 0.36521))
loop_1 = loop_1.threePointArc((-0.05947, 0.35351), (-0.06174, 0.34206))
loop_1 = loop_1.threePointArc((-0.05955, 0.32113), (-0.05935, 0.30569))
loop_1 = loop_1.threePointArc((-0.05874, 0.29866), (-0.0577, 0.29247))
loop_1 = loop_1.lineTo(-0.05484, 0.28028)
loop_1 = loop_1.threePointArc((-0.05486, 0.26044), (-0.05428, 0.24187))
loop_1 = loop_1.threePointArc((-0.05497, 0.20055), (-0.05461, 0.16137))
loop_1 = loop_1.threePointArc((-0.05456, 0.08681), (-0.05506, 0.00965))
loop_1 = loop_1.lineTo(-0.05481, -0.05197)
loop_1 = loop_1.threePointArc((-0.0543, -0.07426), (-0.05465, -0.09699))
loop_1 = loop_1.lineTo(-0.05433, -0.18868)
loop_1 = loop_1.lineTo(-0.05472, -0.24544)
loop_1 = loop_1.lineTo(-0.06348, 0.46222)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.53)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_26_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_26_interval_1.stl')