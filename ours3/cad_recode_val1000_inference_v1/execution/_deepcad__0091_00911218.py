import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-5,0))
r=w0.sketch().segment((-100,-100),(-48,-100)).segment((-48,-70)).segment((-31,-70)).segment((-31,-100)).segment((32,-100)).segment((32,-67)).segment((38,-67)).segment((38,-37)).segment((32,-37)).segment((32,-23)).segment((23,-23)).segment((23,-21)).segment((-31,31)).segment((-31,19)).segment((-33,19)).segment((-33,26)).segment((-54,54)).segment((-100,100)).segment((-100,33)).segment((-31,-32)).segment((-31,-40)).segment((-38,-40)).segment((-38,-37)).segment((-48,-37)).segment((-48,-23)).segment((-50,-23)).segment((-50,-32)).segment((-71,-52)).segment((-66,-57)).segment((-90,-86)).segment((-100,-78)).close().assemble().reset().face(w0.sketch().segment((52,-82),(80,-98)).segment((90,-84)).segment((62,-61)).close().assemble()).finalize().extrude(10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0091_00911218.step')
