import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-4,0))
r=w0.sketch().arc((-95,-17),(-73,-18),(-86,-30)).arc((-72,-39),(-56,-40)).segment((-28,-40)).arc((-21,-39),(-14,-37)).segment((-14,-32)).segment((-12,-32)).segment((-12,-39)).arc((1,-40),(14,-40)).segment((21,-40)).segment((21,-39)).arc((33,-34),(43,-29)).segment((43,-32)).segment((100,-4)).segment((91,12)).segment((91,11)).segment((77,11)).segment((77,19)).segment((43,29)).segment((43,28)).arc((33,34),(21,39)).segment((21,40)).segment((14,40)).arc((1,40),(-12,40)).segment((-19,40)).segment((-19,39)).arc((-31,40),(-43,39)).segment((-43,38)).arc((-85,31),(-95,-17)).assemble().reset().face(w0.sketch().segment((-77,24),(-61,14)).segment((-58,19)).segment((-74,29)).close().assemble(),mode='s').push([(24,0)]).circle(19,mode='s').finalize().extrude(8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__129422_621d0a90_0001.step')
