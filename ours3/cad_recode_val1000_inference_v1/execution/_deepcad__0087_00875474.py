import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,7))
r=w0.sketch().segment((-38,-92),(-27,-92)).segment((-27,-100)).segment((27,-100)).segment((27,-92)).segment((38,-92)).segment((38,-67)).segment((37,-67)).segment((37,-59)).segment((38,-59)).segment((38,-49)).segment((33,-49)).segment((33,-13)).segment((38,-13)).segment((38,25)).segment((37,25)).segment((37,35)).segment((38,35)).segment((38,92)).segment((27,92)).segment((27,100)).segment((-27,100)).segment((-27,92)).segment((-38,92)).segment((-38,72)).arc((-16,60),(-38,48)).close().assemble().push([(0,-46)]).circle(16,mode='s').push([(0,46)]).rect(36,24,mode='s').finalize().extrude(-14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0087_00875474.step')
