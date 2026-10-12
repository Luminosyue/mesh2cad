import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,35))
w1=cq.Workplane('ZX',origin=(0,11,0))
r=w0.sketch().arc((93,-15),(95,-21),(97,-27)).segment((100,-15)).close().assemble().reset().face(w0.sketch().segment((93,13),(98,13)).segment((98,21)).segment((93,21)).arc((94,17),(93,13)).assemble()).finalize().extrude(-72).union(w0.sketch().segment((-100,-7),(-91,-46)).segment((-34,-32)).segment((-34,-46)).segment((34,-47)).segment((34,-42)).segment((33,-42)).segment((33,-38)).segment((34,-38)).segment((34,-37)).segment((33,-37)).segment((33,23)).segment((92,23)).segment((92,47)).segment((-34,47)).segment((-34,38)).segment((-16,38)).segment((-16,37)).segment((-34,37)).segment((-34,23)).segment((-43,23)).segment((-43,11)).segment((-34,11)).segment((-34,10)).segment((-31,10)).close().assemble().finalize().extrude(-4)).union(w1.sketch().arc((-28,-31),(-10,-46),(-11,-70)).segment((-11,-86)).arc((19,-80),(10,-51)).arc((15,-42),(15,-31)).segment((15,-30)).segment((14,-30)).arc((13,-29),(12,-28)).arc((18,-19),(18,-8)).segment((18,33)).segment((-10,33)).segment((-10,-4)).arc((-19,-16),(-19,-31)).close().assemble().finalize().extrude(-2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0046_00464513.step')
