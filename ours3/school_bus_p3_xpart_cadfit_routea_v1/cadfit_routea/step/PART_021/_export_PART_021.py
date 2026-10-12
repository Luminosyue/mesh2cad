import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.65095, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03312, 0.87067)
loop_1 = loop_1.threePointArc((0.03221, 0.86318), (0.09994, 0.85294))
loop_1 = loop_1.threePointArc((0.11306, 0.83722), (0.12341, 0.82081))
loop_1 = loop_1.threePointArc((0.1317, 0.80809), (0.13591, 0.79419))
loop_1 = loop_1.threePointArc((0.14228, 0.77265), (0.145, 0.75071))
loop_1 = loop_1.threePointArc((0.15158, 0.6842), (0.15484, 0.61594))
loop_1 = loop_1.threePointArc((0.1613, 0.51663), (0.16625, 0.41436))
loop_1 = loop_1.threePointArc((0.17144, 0.15789), (0.1595, -0.10783))
loop_1 = loop_1.threePointArc((0.14415, -0.27445), (0.13433, -0.43363))
loop_1 = loop_1.lineTo(0.11476, -0.68521)
loop_1 = loop_1.lineTo(0.10899, -0.74237)
loop_1 = loop_1.lineTo(0.10522, -0.76479)
loop_1 = loop_1.threePointArc((0.10129, -0.77164), (0.09808, -0.77725))
loop_1 = loop_1.threePointArc((0.07486, -0.75462), (0.05245, -0.73473))
loop_1 = loop_1.threePointArc((0.04314, -0.7282), (0.03613, -0.72039))
loop_1 = loop_1.threePointArc((0.02164, -0.68502), (0.01253, -0.65334))
loop_1 = loop_1.threePointArc((-0.00499, -0.60592), (-0.02433, -0.56271))
loop_1 = loop_1.lineTo(-0.04856, -0.48877)
loop_1 = loop_1.threePointArc((-0.0774, -0.40009), (-0.10619, -0.31654))
loop_1 = loop_1.threePointArc((-0.12316, -0.25841), (-0.13901, -0.19869))
loop_1 = loop_1.lineTo(-0.16602, -0.12212)
loop_1 = loop_1.threePointArc((-0.17717, -0.09355), (-0.18647, -0.06429))
loop_1 = loop_1.lineTo(-0.20061, -0.00535)
loop_1 = loop_1.threePointArc((-0.20545, 0.08163), (-0.20672, 0.17113))
loop_1 = loop_1.threePointArc((-0.21083, 0.30194), (-0.21602, 0.4263))
loop_1 = loop_1.threePointArc((-0.21295, 0.5054), (-0.20468, 0.58613))
loop_1 = loop_1.threePointArc((-0.19772, 0.66578), (-0.18647, 0.74701))
loop_1 = loop_1.threePointArc((-0.17582, 0.77562), (-0.16393, 0.80363))
loop_1 = loop_1.lineTo(-0.13485, 0.83736)
loop_1 = loop_1.threePointArc((-0.13001, 0.84399), (-0.124, 0.84807))
loop_1 = loop_1.lineTo(-0.09752, 0.86741)
loop_1 = loop_1.threePointArc((-0.06598, 0.86973), (-0.03431, 0.87062))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.21)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/school_bus_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_021/PART_021.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/school_bus_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_021/PART_021_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
