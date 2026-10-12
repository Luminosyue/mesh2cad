import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,94,0))
r=w0.sketch().segment((-100,-99),(100,-99)).segment((100,99)).segment((7,99)).arc((-25,17),(-100,90)).close().assemble().finalize().extrude(-188).union(w0.sketch().segment((-93,-92),(93,-92)).segment((93,-1)).arc((95,10),(93,21)).segment((93,92)).segment((-93,92)).close().assemble().finalize().extrude(-18))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0076_00763756.step')
