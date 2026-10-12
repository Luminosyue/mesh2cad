import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.36413, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.54292, 0.99865)
loop_1 = loop_1.threePointArc((0.55236, 0.99195), (0.56147, 0.98404))
loop_1 = loop_1.threePointArc((0.56289, 0.97655), (0.56313, 0.97099))
loop_1 = loop_1.threePointArc((0.51716, 0.89322), (0.46542, 0.81703))
loop_1 = loop_1.threePointArc((0.4217, 0.74708), (0.37431, 0.67784))
loop_1 = loop_1.threePointArc((0.34076, 0.61892), (0.30407, 0.56136))
loop_1 = loop_1.threePointArc((0.26284, 0.49122), (0.2156, 0.42322))
loop_1 = loop_1.threePointArc((0.16142, 0.3509), (0.09969, 0.28224))
loop_1 = loop_1.threePointArc((0.042, 0.22055), (-0.02086, 0.16021))
loop_1 = loop_1.threePointArc((-0.08676, 0.10235), (-0.16135, 0.05325))
loop_1 = loop_1.threePointArc((-0.22279, 0.01616), (-0.28723, -0.0178))
loop_1 = loop_1.threePointArc((-0.26428, -0.0446), (-0.23473, -0.0623))
loop_1 = loop_1.threePointArc((-0.11867, -0.14142), (-0.00534, -0.23066))
loop_1 = loop_1.threePointArc((0.11007, -0.34335), (0.22522, -0.46304))
loop_1 = loop_1.threePointArc((0.31405, -0.57716), (0.39832, -0.69948))
loop_1 = loop_1.threePointArc((0.4327, -0.76582), (0.47021, -0.82461))
loop_1 = loop_1.lineTo(0.55164, -0.95509)
loop_1 = loop_1.lineTo(0.56399, -0.97922)
loop_1 = loop_1.threePointArc((0.55986, -0.98689), (0.55644, -0.99259))
loop_1 = loop_1.threePointArc((0.54902, -0.99636), (0.54371, -0.99918))
loop_1 = loop_1.threePointArc((0.53061, -0.9905), (0.52112, -0.97979))
loop_1 = loop_1.threePointArc((0.44306, -0.89699), (0.36532, -0.81025))
loop_1 = loop_1.threePointArc((0.30971, -0.74026), (0.25586, -0.67579))
loop_1 = loop_1.lineTo(0.14663, -0.54921)
loop_1 = loop_1.threePointArc((0.09154, -0.48478), (0.0363, -0.4275))
loop_1 = loop_1.threePointArc((-0.04476, -0.35922), (-0.12491, -0.29973))
loop_1 = loop_1.threePointArc((-0.19199, -0.25268), (-0.25578, -0.20991))
loop_1 = loop_1.threePointArc((-0.32897, -0.17399), (-0.39857, -0.14257))
loop_1 = loop_1.threePointArc((-0.47071, -0.10265), (-0.54104, -0.05765))
loop_1 = loop_1.threePointArc((-0.5543, -0.04953), (-0.56347, -0.03865))
loop_1 = loop_1.threePointArc((-0.55247, -0.0245), (-0.53776, -0.01464))
loop_1 = loop_1.threePointArc((-0.45546, 0.04582), (-0.3793, 0.10435))
loop_1 = loop_1.threePointArc((-0.22702, 0.21116), (-0.0837, 0.31467))
loop_1 = loop_1.threePointArc((0.0244, 0.40597), (0.11299, 0.50647))
loop_1 = loop_1.threePointArc((0.19396, 0.60728), (0.27995, 0.70837))
loop_1 = loop_1.lineTo(0.41522, 0.87046)
loop_1 = loop_1.threePointArc((0.47361, 0.93361), (0.53487, 0.99628))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.73)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_058/PART_058.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_058/PART_058_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
