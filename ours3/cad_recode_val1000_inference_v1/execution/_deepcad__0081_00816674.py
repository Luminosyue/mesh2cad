import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(19,0,0))
r=w0.sketch().segment((-69,-100),(69,-100)).segment((69,-65)).segment((68,-65)).segment((68,-63)).segment((69,-63)).segment((69,100)).segment((-69,100)).segment((-69,57)).segment((-39,57)).segment((-39,49)).segment((-69,49)).segment((-69,-10)).segment((-39,14)).segment((-39,-26)).segment((-69,-26)).close().assemble().reset().face(w0.sketch().segment((-33,-65),(27,-65)).segment((27,-50)).segment((68,-50)).segment((68,43)).segment((-10,43)).segment((-10,19)).segment((-33,-1)).close().assemble(),mode='s').finalize().extrude(-38).union(w0.sketch().arc((-43,-17),(1,-37),(43,-10)).segment((69,-10)).segment((69,50)).segment((43,50)).arc((1,72),(-43,52)).close().assemble().finalize().extrude(-3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0081_00816674.step')
