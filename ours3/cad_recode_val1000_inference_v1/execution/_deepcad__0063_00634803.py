import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(83,0,0))
w1=cq.Workplane('ZX',origin=(0,-74,0))
r=w0.sketch().arc((-74,-49),(-55,-47),(-37,-41)).segment((-55,-41)).segment((-55,41)).arc((-65,45),(-74,49)).close().assemble().reset().face(w0.sketch().arc((-46,-37),(-37,-35),(-29,-32)).arc((-20,-23),(-15,-12)).arc((18,0),(-15,12)).arc((-20,23),(-28,32)).arc((-30,35),(-32,37)).segment((-32,32)).arc((-19,-23),(-46,-37)).assemble()).finalize().extrude(-91).union(w0.sketch().segment((-53,-13),(-18,-13)).segment((-18,-30)).segment((55,-30)).segment((55,49)).segment((24,49)).arc((23,47),(22,49)).segment((-18,49)).segment((-18,32)).segment((-53,32)).close().assemble().finalize().extrude(17)).union(w1.sketch().segment((-49,-100),(49,-100)).segment((49,-74)).arc((0,-84),(-49,-74)).close().assemble().finalize().extrude(149))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0063_00634803.step')
