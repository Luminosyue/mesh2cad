import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-6,0))
w1=cq.Workplane('YZ',origin=(22,0,0))
r=w0.sketch().segment((-95,-32),(-74,-32)).segment((-74,-27)).arc((-67,-27),(-60,-25)).segment((-60,-32)).segment((-26,-32)).segment((-26,-31)).segment((-21,-31)).segment((-21,-21)).arc((-14,-23),(-7,-23)).segment((-7,-32)).segment((12,-32)).segment((12,-29)).segment((31,-30)).segment((31,-22)).segment((33,-22)).arc((34,-17),(38,-11)).segment((38,4)).segment((35,4)).arc((23,10),(12,4)).segment((-7,4)).segment((-7,10)).segment((-47,10)).segment((-47,8)).segment((-93,10)).segment((-93,3)).arc((-100,-11),(-95,-27)).close().assemble().finalize().extrude(-2).union(w0.sketch().segment((-38,22),(-26,22)).segment((-26,24)).segment((-38,32)).close().assemble().finalize().extrude(14)).union(w1.sketch().segment((-2,86),(1,86)).arc((4,90),(8,92)).segment((8,100)).segment((6,100)).segment((6,96)).segment((-2,96)).close().assemble().push([(5,93)]).circle(2,mode='s').finalize().extrude(10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00585708.step')
