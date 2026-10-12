import cadquery as cq
import math
import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.8, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01311, 0.31337)
loop_1 = loop_1.lineTo(0.02529, 0.31248)
loop_1 = loop_1.threePointArc((0.04402, 0.31157), (0.05447, 0.31019))
loop_1 = loop_1.lineTo(0.07219, 0.30871)
loop_1 = loop_1.threePointArc((0.09512, 0.3042), (0.11765, 0.29705))
loop_1 = loop_1.threePointArc((0.14851, 0.28356), (0.17633, 0.26337))
loop_1 = loop_1.threePointArc((0.20676, 0.23494), (0.2316, 0.20026))
loop_1 = loop_1.threePointArc((0.2863, 0.08108), (0.31003, -0.05271))
loop_1 = loop_1.threePointArc((0.31218, -0.08736), (0.31152, -0.12275))
loop_1 = loop_1.threePointArc((0.30859, -0.13941), (0.30485, -0.15583))
loop_1 = loop_1.threePointArc((0.29553, -0.19026), (0.28211, -0.22408))
loop_1 = loop_1.threePointArc((0.26379, -0.25542), (0.24248, -0.2857))
loop_1 = loop_1.threePointArc((0.22945, -0.30246), (0.21476, -0.31786))
loop_1 = loop_1.threePointArc((0.19577, -0.33681), (0.17423, -0.35337))
loop_1 = loop_1.threePointArc((0.11444, -0.38432), (0.04905, -0.40739))
loop_1 = loop_1.threePointArc((0.01517, -0.41263), (-0.01968, -0.41056))
loop_1 = loop_1.threePointArc((-0.05511, -0.40524), (-0.0898, -0.39366))
loop_1 = loop_1.threePointArc((-0.09978, -0.38936), (-0.10894, -0.38401))
loop_1 = loop_1.lineTo(-0.157, -0.34833)
loop_1 = loop_1.threePointArc((-0.17721, -0.32827), (-0.19472, -0.30523))
loop_1 = loop_1.lineTo(-0.21286, -0.28145)
loop_1 = loop_1.threePointArc((-0.23676, -0.23703), (-0.25566, -0.18882))
loop_1 = loop_1.threePointArc((-0.26946, -0.15041), (-0.28172, -0.11048))
loop_1 = loop_1.threePointArc((-0.29257, -0.05247), (-0.29795, 0.00797))
loop_1 = loop_1.threePointArc((-0.29871, 0.02857), (-0.29795, 0.04928))
loop_1 = loop_1.threePointArc((-0.2909, 0.08932), (-0.27892, 0.12913))
loop_1 = loop_1.threePointArc((-0.26037, 0.1781), (-0.23664, 0.22635))
loop_1 = loop_1.threePointArc((-0.22419, 0.24583), (-0.21002, 0.26441))
loop_1 = loop_1.threePointArc((-0.19909, 0.2742), (-0.18725, 0.2826))
loop_1 = loop_1.threePointArc((-0.1715, 0.2894), (-0.15494, 0.2937))
loop_1 = loop_1.threePointArc((-0.1378, 0.29863), (-0.1222, 0.30375))
loop_1 = loop_1.threePointArc((-0.0981, 0.30887), (-0.07332, 0.31075))
loop_1 = loop_1.threePointArc((-0.04383, 0.3125), (-0.01383, 0.31333))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.94)

result = solid_1


try:
    _shape = locals().get('result') or locals().get('final_result')
    if _shape is None:
        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asics_gelace_pro_pearl_whitepink_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_008/PART_008.step', 'STEP')
    cq.exporters.export(_shape, r'/data/home/cuiyuehan/project/mesh2cad/ours3/asics_gelace_pro_pearl_whitepink_p3_xpart_cadfit_routea_v1/cadfit_routea/step/PART_008/PART_008_reconstructed.stl', 'STL')
    print('STEP_OK')
except Exception as e:
    print(f'STEP_FAIL {e}')
