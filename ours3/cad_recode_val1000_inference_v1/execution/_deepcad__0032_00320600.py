import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('XY',origin=(0,0,-25))
r=w0.sketch().segment((-30,39),(-28,20)).arc((-27,27),(-22,32)).close().assemble().reset().face(w0.sketch().arc((-27,-27),(-21,-39),(-8,-36)).arc((12,-32),(28,-28)).segment((27,-27)).arc((19,-20),(12,-9)).close().assemble()).reset().face(w0.sketch().segment((-27,15),(-7,15)).arc((-17,20),(-27,27)).close().assemble()).finalize().extrude(38).union(w0.sketch().segment((-29,30),(-27,3)).arc((-27,-4),(-26,-11)).segment((-25,-39)).segment((29,-29)).segment((25,-23)).arc((15,-12),(7,-1)).arc((-12,19),(-29,39)).close().assemble().finalize().extrude(200)).union(w1.sketch().arc((-39,38),(-34,28),(-39,17)).segment((-39,16)).arc((-23,-1),(-39,-18)).segment((-39,-20)).arc((24,-1),(-39,18)).close().assemble().finalize().extrude(11))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0032_00320600.step')
