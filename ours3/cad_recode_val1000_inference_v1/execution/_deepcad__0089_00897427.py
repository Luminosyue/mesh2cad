import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-20,0))
r=w0.sketch().segment((-100,-59),(100,-59)).segment((100,59)).segment((-100,59)).segment((-100,33)).segment((-98,33)).segment((-98,30)).segment((-100,30)).close().assemble().reset().face(w0.sketch().segment((-98,-30),(-48,-30)).segment((-48,-53)).segment((-42,-53)).segment((-42,-30)).segment((-12,-30)).segment((-12,-59)).segment((12,-59)).segment((12,-30)).segment((42,-30)).segment((42,-53)).segment((98,-53)).segment((98,53)).segment((12,53)).segment((12,30)).segment((42,30)).segment((42,59)).segment((-42,59)).segment((-42,53)).segment((-48,53)).segment((-48,33)).segment((-98,33)).close().assemble(),mode='s').finalize().extrude(39)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0089_00897427.step')
