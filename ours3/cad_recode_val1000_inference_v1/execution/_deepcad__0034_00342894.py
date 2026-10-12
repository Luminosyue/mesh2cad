import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-93,0))
r=w0.sketch().segment((-50,-15),(-30,-15)).segment((-30,-30)).segment((45,-30)).segment((45,-15)).segment((50,-15)).segment((50,15)).segment((45,15)).segment((45,30)).segment((-30,30)).segment((-30,15)).segment((-50,15)).close().assemble().push([(20,0)]).circle(14,mode='s').finalize().extrude(200).union(w1.sketch().arc((-15,-30),(25,0),(-15,30)).segment((-15,15)).arc((-4,0),(-15,-15)).close().assemble().finalize().extrude(70))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0034_00342894.step')
