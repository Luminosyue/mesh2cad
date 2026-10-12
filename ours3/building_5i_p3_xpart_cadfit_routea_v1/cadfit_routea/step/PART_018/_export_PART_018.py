import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01571, -0.79996, 0.00105), normal=(1e-05, 1.0, 0.00015), xDir=(1.0, -1e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.95073, 0.13295)
loop_1 = loop_1.lineTo(-1.01244, 0.13195)
loop_1 = loop_1.lineTo(-1.01553, 0.12154)
loop_1 = loop_1.lineTo(-1.01531, -0.12751)
loop_1 = loop_1.lineTo(-1.00133, -0.13044)
loop_1 = loop_1.lineTo(0.9826, -0.12859)
loop_1 = loop_1.lineTo(0.98397, 0.1265)
loop_1 = loop_1.lineTo(0.97357, 0.13284)
loop_1 = loop_1.lineTo(0.95302, 0.13289)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.6)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_018/PART_018.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_018/PART_018_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
