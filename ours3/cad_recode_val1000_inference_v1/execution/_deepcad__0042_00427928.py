import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-33,0,0))
r=w0.sketch().segment((-100,-59),(100,-59)).segment((100,-26)).segment((33,-26)).segment((33,59)).segment((-33,59)).segment((-33,-26)).segment((-100,-26)).close().assemble().push([(0,-42.5)]).rect(10,13,mode='s').push([(0,-15.5)]).rect(10,13,mode='s').push([(85,-56)]).circle(3,mode='s').finalize().extrude(47).union(w0.sketch().segment((-98,-40),(-33,-40)).segment((-33,-26)).segment((33,-26)).segment((33,47)).segment((-33,47)).segment((-33,-25)).segment((-98,-25)).close().assemble().push([(0,10)]).circle(14,mode='s').finalize().extrude(66))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00427928.step')
