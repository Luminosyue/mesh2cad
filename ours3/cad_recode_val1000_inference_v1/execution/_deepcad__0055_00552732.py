import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-33,0))
w1=cq.Workplane('XY',origin=(0,0,10))
r=w0.sketch().segment((-16,-17),(-13,-23)).segment((-11,-22)).arc((-13,-17),(-13,-12)).arc((-14,-14),(-16,-17)).assemble().reset().face(w0.sketch().arc((-11,-22),(-10,-27),(-10,-31)).segment((17,-15)).segment((13,-8)).close().assemble()).finalize().extrude(-47).union(w0.sketch().push([(0,-14)]).circle(17).circle(16,mode='s').finalize().extrude(89)).union(w0.workplane(offset=133/2).moveTo(0,13).cylinder(133,11)).union(w1.sketch().arc((-31,-77),(-10,-82),(-6,-100)).arc((1,-92),(3,-82)).arc((16,-58),(-12,-60)).arc((-25,-63),(-31,-77)).assemble().push([(0,-69)]).circle(15,mode='s').finalize().extrude(-18))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0055_00552732.step')
