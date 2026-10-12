import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
w1=cq.Workplane('ZX',origin=(0,48,0))
r=w0.sketch().segment((-75,-74),(41,-55)).segment((39,-43)).segment((-75,-70)).close().assemble().finalize().extrude(194).union(w0.sketch().segment((-74,-74),(-70,-74)).segment((-70,-75)).segment((70,-75)).segment((70,-74)).segment((75,-74)).segment((75,74)).segment((70,74)).segment((70,75)).segment((69,75)).arc((20,19),(-44,-30)).segment((-44,-39)).segment((-49,-39)).arc((-60,-59),(-74,-74)).assemble().finalize().extrude(200)).union(w1.sketch().arc((-50,-60),(10,-88),(70,-60)).segment((50,-60)).segment((50,30)).segment((32,30)).segment((32,60)).segment((34,60)).arc((10,70),(-16,73)).arc((47,-18),(-50,-60)).assemble().finalize().extrude(-24))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0040_00406437.step')
