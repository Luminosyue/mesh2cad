import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-67,0))
r=w0.sketch().segment((-56,-100),(-28,-100)).segment((-28,-28)).segment((15,-28)).segment((15,-100)).segment((28,-100)).segment((28,-33)).arc((19,28),(-28,-10)).segment((-28,63)).segment((-56,63)).close().assemble().finalize().extrude(24).union(w0.sketch().segment((-56,-100),(56,-100)).segment((56,-43)).segment((55,-43)).segment((55,-40)).segment((56,-40)).segment((56,96)).segment((36,96)).segment((36,100)).segment((-56,100)).segment((-56,87)).segment((-55,87)).segment((-55,83)).segment((-56,83)).segment((-56,-40)).segment((-55,-40)).segment((-55,-43)).segment((-56,-43)).close().assemble().push([(22,28)]).circle(34,mode='s').reset().face(w0.sketch().segment((-28,78),(-24,77)).segment((-22,85)).segment((-26,86)).close().assemble(),mode='s').finalize().extrude(134))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0073_00738783.step')
