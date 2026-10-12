import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-2,0))
r=w0.sketch().segment((-13,58),(-12,58)).segment((-12,30)).segment((-11,30)).segment((-11,29)).segment((-12,29)).segment((-12,-8)).segment((-11,-8)).segment((-11,-39)).segment((11,-39)).segment((11,-8)).segment((13,42)).segment((12,42)).segment((12,74)).segment((13,74)).segment((13,76)).segment((12,76)).segment((12,100)).segment((-12,100)).segment((-12,96)).segment((-11,96)).segment((-11,95)).segment((-12,95)).segment((-12,76)).segment((-13,76)).close().assemble().push([(0,-82.5)]).rect(24,35).finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0041_00415067.step')
