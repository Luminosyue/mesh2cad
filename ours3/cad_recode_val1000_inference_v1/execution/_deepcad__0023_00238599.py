import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,6,0))
r=w0.sketch().push([(-92,-68)]).circle(5).push([(-92,-67.5)]).rect(4,5,mode='s').reset().face(w0.sketch().segment((-100,68),(-96,68)).segment((-96,63)).segment((91,63)).segment((91,-63)).segment((-96,-63)).segment((-96,-72)).segment((87,-72)).segment((87,-67)).segment((91,-67)).segment((91,-66)).segment((100,-66)).segment((100,68)).segment((97,68)).segment((97,72)).segment((-100,72)).close().assemble()).finalize().extrude(-12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0023_00238599.step')
