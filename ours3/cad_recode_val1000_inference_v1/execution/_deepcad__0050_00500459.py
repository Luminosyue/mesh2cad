import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-7,0))
r=w0.sketch().segment((-100,-74),(-93,-74)).segment((-93,-86)).segment((93,-86)).segment((93,-74)).segment((100,-74)).segment((100,74)).segment((93,74)).segment((93,86)).segment((-93,86)).segment((-93,74)).segment((-100,74)).close().assemble().reset().face(w0.sketch().segment((-90,39),(-48,-33)).segment((-12,-12)).segment((-12,-33)).segment((-39,-46)).segment((-59,-10)).segment((12,-64)).segment((12,-59)).segment((15,-59)).segment((15,-66)).segment((39,-79)).segment((59,-43)).segment((35,-30)).segment((61,-17)).segment((41,15)).segment((90,36)).segment((48,80)).segment((12,50)).segment((12,39)).segment((10,39)).segment((10,46)).segment((-12,36)).segment((-12,12)).segment((-39,10)).segment((-59,10)).segment((-59,22)).segment((-48,22)).segment((-59,36)).segment((-59,46)).close().assemble(),mode='s').push([(-27,66)]).rect(44,14,mode='s').finalize().extrude(14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0050_00500459.step')
