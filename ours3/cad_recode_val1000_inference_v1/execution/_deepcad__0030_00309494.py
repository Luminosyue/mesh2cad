import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,42,0))
w1=cq.Workplane('ZX',origin=(0,21,0))
r=w0.sketch().segment((-34,-100),(33,-100)).segment((33,-79)).segment((-8,-79)).segment((-8,63)).segment((17,63)).segment((17,88)).segment((0,88)).segment((0,100)).segment((-33,100)).segment((-33,50)).segment((-20,50)).segment((-20,23)).segment((-33,23)).segment((-33,-38)).segment((-34,-38)).segment((-34,-40)).segment((-33,-40)).segment((-33,-74)).segment((-34,-74)).close().assemble().finalize().extrude(-84).union(w0.sketch().segment((-21,28),(-14,28)).arc((-18,44),(-14,60)).segment((-21,60)).close().assemble().finalize().extrude(-1)).union(w1.sketch().push([(-10,44)]).circle(19).push([(-10,44.5)]).rect(16,23,mode='s').finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00309494.step')
