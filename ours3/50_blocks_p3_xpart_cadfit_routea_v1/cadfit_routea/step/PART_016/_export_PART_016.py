import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.95), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28406, 0.01019)
loop_1 = loop_1.lineTo(-0.28323, -0.01455)
loop_1 = loop_1.lineTo(-0.28002, -0.03532)
loop_1 = loop_1.threePointArc((-0.26983, -0.07032), (-0.25706, -0.10229))
loop_1 = loop_1.threePointArc((-0.23449, -0.13986), (-0.20929, -0.17284))
loop_1 = loop_1.threePointArc((-0.18051, -0.20052), (-0.15042, -0.22336))
loop_1 = loop_1.threePointArc((-0.12499, -0.23919), (-0.09986, -0.25202))
loop_1 = loop_1.threePointArc((-0.08097, -0.25918), (-0.06291, -0.26444))
loop_1 = loop_1.threePointArc((-0.02822, -0.27143), (0.0051, -0.27418))
loop_1 = loop_1.threePointArc((0.02439, -0.27259), (0.04213, -0.26955))
loop_1 = loop_1.threePointArc((0.07006, -0.26325), (0.09559, -0.25456))
loop_1 = loop_1.threePointArc((0.1176, -0.24469), (0.13763, -0.23426))
loop_1 = loop_1.threePointArc((0.17816, -0.20668), (0.21203, -0.1748))
loop_1 = loop_1.threePointArc((0.22959, -0.15388), (0.24485, -0.13326))
loop_1 = loop_1.lineTo(0.2554, -0.11559)
loop_1 = loop_1.threePointArc((0.26545, -0.09218), (0.27369, -0.06974))
loop_1 = loop_1.lineTo(0.27774, -0.05174)
loop_1 = loop_1.threePointArc((0.28128, -0.01795), (0.28303, 0.01406))
loop_1 = loop_1.threePointArc((0.28185, 0.02591), (0.28036, 0.03664))
loop_1 = loop_1.threePointArc((0.27207, 0.07086), (0.26052, 0.10204))
loop_1 = loop_1.threePointArc((0.25439, 0.11699), (0.24669, 0.12978))
loop_1 = loop_1.threePointArc((0.229, 0.15678), (0.20924, 0.17993))
loop_1 = loop_1.threePointArc((0.17007, 0.215), (0.12789, 0.24173))
loop_1 = loop_1.threePointArc((0.10373, 0.25366), (0.07996, 0.26244))
loop_1 = loop_1.threePointArc((0.02558, 0.27265), (-0.02698, 0.27212))
loop_1 = loop_1.threePointArc((-0.0752, 0.26128), (-0.11862, 0.24359))
loop_1 = loop_1.threePointArc((-0.132, 0.23688), (-0.14376, 0.22962))
loop_1 = loop_1.threePointArc((-0.17362, 0.20946), (-0.19997, 0.18792))
loop_1 = loop_1.threePointArc((-0.21165, 0.17653), (-0.22107, 0.16471))
loop_1 = loop_1.threePointArc((-0.2464, 0.12842), (-0.26585, 0.09125))
loop_1 = loop_1.threePointArc((-0.2699, 0.08013), (-0.27311, 0.06984))
loop_1 = loop_1.threePointArc((-0.27841, 0.04746), (-0.2825, 0.02632))
loop_1 = loop_1.lineTo(-0.28399, 0.01072)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.91)
result = solid_1

# ===== Operation Script =====
plane_op_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_op_1 = cq.Workplane(plane_op_1)
loop_1 = sketch_op_1.moveTo(-0.01273, 0.27348)
loop_1 = loop_1.threePointArc((-0.00065, 0.25934), (0.01141, 0.24418))
loop_1 = loop_1.lineTo(0.09461, 0.14107)
loop_1 = loop_1.lineTo(-0.16952, -0.07144)
loop_1 = loop_1.lineTo(-0.27529, 0.0605)
loop_1 = loop_1.threePointArc((-0.2731, 0.06894), (-0.27047, 0.07727))
loop_1 = loop_1.lineTo(-0.02894, 0.27154)
loop_1 = loop_1.threePointArc((-0.02086, 0.27265), (-0.01275, 0.27343))
loop_1 = loop_1.close()
sketch_op_1=sketch_op_1.add(loop_1)
solid_op_1 = sketch_op_1.extrude(2.0)
result_op = solid_op_1

# ===== Combine using union =====
final_result = result.add(result_op)


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/50_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_016/PART_016.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/50_blocks_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_016/PART_016_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
