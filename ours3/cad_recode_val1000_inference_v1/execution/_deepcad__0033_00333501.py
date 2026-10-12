import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
w1=cq.Workplane('ZX',origin=(0,-31,0))
r=w0.sketch().segment((51,17),(97,17)).segment((97,16)).segment((100,17)).segment((53,44)).segment((51,44)).close().assemble().finalize().extrude(-59).union(w0.sketch().push([(-16.5,-27)]).rect(19,36).push([(-17,-27)]).circle(4,mode='s').finalize().extrude(-23)).union(w0.sketch().arc((-93,-31),(-86,-33),(-79,-34)).segment((-57,-34)).segment((-57,-31)).segment((13,-31)).segment((13,-34)).segment((57,-34)).segment((57,-31)).segment((60,-31)).segment((60,-34)).segment((99,-34)).arc((78,-1),(39,-10)).segment((39,-8)).segment((13,-8)).segment((13,-10)).arc((-17,-27),(-46,-10)).segment((-57,-10)).segment((-57,-8)).segment((-93,-8)).close().assemble().finalize().extrude(31)).union(w1.sketch().segment((-23,-28),(-21,-28)).segment((-21,-100)).segment((21,-100)).segment((21,-69)).segment((59,-69)).segment((59,-7)).segment((55,-7)).segment((55,44)).segment((43,44)).segment((43,64)).segment((30,64)).segment((30,100)).segment((0,100)).segment((0,-7)).segment((-21,-7)).segment((-21,-26)).segment((-23,-26)).close().assemble().finalize().extrude(23))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0033_00333501.step')
