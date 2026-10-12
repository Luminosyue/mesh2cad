import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,42,0))
r=w0.sketch().arc((-98,11),(-74,-66),(-1,-90)).arc((96,-25),(41,89)).arc((27,95),(12,97)).arc((-1,98),(-14,97)).arc((-24,95),(-33,93)).arc((-40,90),(-46,87)).arc((-50,85),(-53,83)).arc((-84,51),(-98,11)).assemble().push([(1,-29)]).circle(61,mode='s').reset().face(w0.sketch().arc((-10,59),(1,59),(12,57)).arc((1,60),(-10,59)).assemble(),mode='s').finalize().extrude(-84).union(w0.workplane(offset=-54/2).cylinder(54,17)).union(w0.sketch().segment((-100,3),(-55,-32)).arc((-54,18),(-14,50)).segment((-14,35)).segment((14,35)).segment((14,50)).arc((47,34),(74,6)).segment((100,36)).segment((55,72)).arc((44,76),(34,83)).segment((14,97)).segment((14,88)).segment((-14,88)).segment((-14,73)).arc((-47,88),(-74,62)).segment((-76,63)).close().assemble().reset().face(w0.sketch().arc((-55,-35),(-45,-88),(-1,-88)).arc((-31,-74),(-55,-50)).close().assemble()).finalize().extrude(-55))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00024544.step')
