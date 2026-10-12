import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,15,0))
r=w0.sketch().segment((-94,-35),(-67,-29)).segment((-48,-43)).segment((-35,-43)).segment((-35,-55)).segment((-11,-64)).segment((-35,-88)).segment((-35,-93)).arc((-24,-97),(-11,-99)).segment((-11,-96)).arc((0,-97),(11,-96)).segment((11,-99)).arc((33,-94),(52,-85)).segment((14,-53)).segment((11,-53)).segment((11,-51)).segment((10,-51)).segment((10,-49)).segment((11,-49)).segment((11,-46)).segment((52,-46)).arc((72,-25),(94,-35)).segment((96,-35)).arc((100,0),(96,35)).segment((96,24)).segment((85,24)).segment((85,49)).segment((87,49)).arc((67,73),(35,85)).segment((35,93)).arc((0,97),(-35,93)).segment((-35,95)).arc((-92,39),(-94,-35)).assemble().reset().face(w0.sketch().segment((-96,-31),(-67,-31)).segment((-87,-21)).segment((-48,39)).segment((-96,39)).close().assemble()).reset().face(w0.sketch().segment((-35,39),(-15,29)).segment((-15,39)).close().assemble()).finalize().extrude(-30)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0056_00563143.step')
