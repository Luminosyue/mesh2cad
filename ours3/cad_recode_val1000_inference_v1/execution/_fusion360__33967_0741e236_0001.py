import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-50))
w1=cq.Workplane('ZX',origin=(0,38,0))
r=w0.sketch().segment((-35,-61),(37,-61)).segment((37,-40)).arc((67,0),(37,40)).segment((37,61)).segment((-13,61)).segment((-13,52)).arc((-65,7),(-35,-50)).close().assemble().finalize().extrude(-50).union(w0.sketch().arc((-37,34),(-49,-10),(-23,-44)).arc((-1,-50),(20,-45)).arc((27,-42),(34,-37)).arc((50,0),(25,38)).arc((24,42),(22,45)).segment((22,46)).segment((21,46)).arc((0,50),(-21,46)).segment((-22,46)).segment((-22,45)).arc((-29,41),(-35,34)).assemble().finalize().extrude(150)).union(w1.sketch().arc((-16,30),(37,20),(73,-22)).arc((64,44),(-4,38)).arc((-10,35),(-16,30)).assemble().finalize().extrude(-7))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__33967_0741e236_0001.step')
