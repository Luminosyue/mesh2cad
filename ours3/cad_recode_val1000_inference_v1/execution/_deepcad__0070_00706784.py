import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-33,0))
r=w0.sketch().segment((-50,-100),(-29,-100)).segment((-29,-89)).segment((16,-89)).segment((16,-100)).segment((50,-100)).segment((50,100)).segment((-50,100)).close().assemble().reset().face(w0.sketch().segment((-50,-84),(-49,-84)).arc((-45,-86),(-41,-84)).segment((-40,-84)).segment((-40,-82)).segment((-41,-82)).arc((-45,-80),(-49,-82)).segment((-50,-82)).close().assemble(),mode='s').push([(-28,76)]).circle(2,mode='s').push([(0,0)]).circle(14,mode='s').push([(48,-50)]).circle(2,mode='s').finalize().extrude(66)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0070_00706784.step')
