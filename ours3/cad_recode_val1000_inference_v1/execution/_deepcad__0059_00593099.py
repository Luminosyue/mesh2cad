import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,11,0))
r=w0.sketch().segment((-49,-63),(-34,-63)).arc((10,-99),(48,-54)).arc((30,-48),(49,-47)).segment((49,-33)).arc((33,-38),(25,-24)).arc((-29,-63),(11,-19)).arc((-1,-14),(-11,-7)).segment((-11,4)).segment((-15,4)).segment((-15,15)).segment((-11,15)).segment((-11,50)).segment((49,50)).segment((49,83)).segment((32,83)).segment((32,100)).segment((-49,100)).segment((-49,15)).segment((-49,4)).close().assemble().finalize().extrude(-22).union(w0.sketch().segment((-48,-64),(-41,-64)).arc((-3,-98),(36,-64)).segment((44,-64)).segment((44,-33)).segment((36,-33)).arc((-3,-1),(-41,-33)).segment((-48,-33)).close().assemble().push([(-3,-55)]).circle(28,mode='s').finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0059_00593099.step')
