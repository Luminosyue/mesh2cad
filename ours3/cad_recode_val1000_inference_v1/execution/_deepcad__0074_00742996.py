import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,36,0))
r=w0.sketch().segment((-100,-18),(9,-18)).segment((9,-55)).segment((100,-55)).segment((100,55)).segment((9,55)).segment((9,18)).segment((-100,18)).close().assemble().push([(54,0)]).circle(7,mode='s').finalize().extrude(-72).union(w0.sketch().segment((-94,-18),(9,-18)).segment((9,-43)).segment((51,-43)).segment((51,-1)).segment((89,-36)).segment((94,-31)).segment((51,14)).segment((51,43)).segment((9,43)).segment((9,11)).segment((-9,26)).segment((-14,20)).segment((9,1)).segment((9,-18)).segment((-94,-18)).close().assemble().finalize().extrude(-1))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00742996.step')
