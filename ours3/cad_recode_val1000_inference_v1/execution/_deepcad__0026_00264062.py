import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-33))
r=w0.sketch().segment((-100,-47),(-87,-47)).segment((-87,-50)).segment((96,-50)).segment((96,-47)).segment((100,-47)).segment((100,47)).segment((96,47)).segment((96,50)).segment((-87,50)).segment((-87,47)).segment((-100,47)).close().assemble().push([(14,0)]).circle(38,mode='s').finalize().extrude(33).union(w0.sketch().segment((-100,-17),(-33,-17)).arc((-25,-16),(-17,-17)).segment((38,-17)).arc((33,-16),(27,-16)).segment((27,16)).segment((100,16)).segment((100,50)).segment((-100,50)).close().assemble().finalize().extrude(66))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00264062.step')
