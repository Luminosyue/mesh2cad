import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,40,0))
r=w0.sketch().segment((-45,-100),(15,-100)).segment((15,-80)).segment((33,-80)).segment((33,-79)).segment((15,-79)).segment((15,-78)).arc((-10,-49),(15,-20)).segment((15,100)).segment((-45,100)).close().assemble().reset().face(w0.sketch().segment((-45,-78),(-45,-23)).arc((-49,-51),(-40,-78)).close().assemble(),mode='s').reset().face(w0.sketch().arc((33,-78),(38,-75),(42,-71)).arc((43,-69),(45,-69)).segment((45,-4)).segment((33,-4)).close().assemble()).finalize().extrude(-80).union(w0.sketch().segment((-45,-100),(15,-100)).segment((15,-66)).arc((26,-34),(15,-2)).segment((15,100)).segment((-45,100)).segment((-45,-2)).arc((-55,-34),(-45,-66)).close().assemble().push([(-15,-34)]).circle(29,mode='s').finalize().extrude(-70))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0088_00884680.step')
