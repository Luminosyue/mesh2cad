import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-20,0))
r=w0.sketch().segment((-100,-40),(54,-40)).segment((54,-39)).segment((57,-39)).segment((57,-40)).segment((100,-40)).segment((100,40)).segment((-100,40)).close().assemble().reset().face(w0.sketch().segment((-92,-39),(-89,-39)).segment((-89,-40)).segment((-86,-40)).segment((-86,-39)).segment((-83,-39)).segment((-83,-34)).segment((-86,-34)).segment((-86,-33)).segment((-89,-33)).segment((-89,-34)).segment((-92,-34)).close().assemble(),mode='s').push([(-56,30)]).circle(10,mode='s').push([(80,26)]).circle(8,mode='s').finalize().extrude(40)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00262817.step')
