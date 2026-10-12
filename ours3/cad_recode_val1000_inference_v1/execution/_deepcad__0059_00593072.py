import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-4,0))
r=w0.sketch().segment((-100,8),(-95,-8)).segment((-46,-8)).arc((-32,-6),(-18,-8)).segment((32,-8)).arc((31,-6),(30,-5)).segment((30,-6)).segment((28,-6)).segment((28,-5)).arc((26,0),(28,5)).segment((28,6)).segment((30,6)).segment((30,5)).arc((31,4),(32,2)).segment((32,8)).close().assemble().reset().face(w0.sketch().segment((-98,8),(-58,8)).arc((-78,10),(-98,8)).assemble()).reset().face(w0.sketch().segment((48,-8),(100,-8)).segment((100,8)).segment((48,8)).arc((51,0),(48,-8)).assemble()).finalize().extrude(7)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0059_00593072.step')
