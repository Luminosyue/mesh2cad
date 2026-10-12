import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-20,0))
r=w0.sketch().segment((-52,45),(-52,47)).arc((-99,-10),(-34,-40)).segment((-34,-45)).segment((55,-45)).segment((55,-44)).arc((99,-9),(75,41)).segment((75,45)).close().assemble().reset().face(w0.sketch().segment((-34,-10),(-34,10)).arc((-36,0),(-34,-10)).assemble(),mode='s').reset().face(w0.sketch().arc((-20,-44),(15,-43),(43,-21)).arc((94,1),(42,22)).arc((16,41),(-17,44)).segment((17,16)).arc((30,-6),(55,-10)).segment((55,-44)).close().assemble(),mode='s').finalize().extrude(39).union(w0.sketch().segment((-100,-7),(-84,9)).arc((-70,36),(-43,23)).segment((-27,38)).arc((-78,39),(-100,-7)).assemble().reset().face(w0.sketch().arc((-97,-16),(-84,-34),(-64,-44)).close().assemble()).finalize().extrude(40))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0044_00445134.step')
