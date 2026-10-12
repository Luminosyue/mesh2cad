import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-23,0))
r=w0.sketch().arc((-23,-16),(-45,-60),(-10,-98)).segment((-10,-100)).segment((-2,-100)).segment((-2,-98)).arc((11,-87),(17,-70)).segment((23,-69)).segment((18,-40)).segment((12,-41)).arc((8,-37),(3,-34)).segment((22,-34)).segment((18,-12)).close().assemble().push([(-1,-54)]).circle(12,mode='s').finalize().extrude(31).union(w0.sketch().segment((-45,-60),(-30,-88)).segment((-10,-77)).arc((-11,-53),(11,-48)).segment((11,-62)).segment((13,-61)).arc((26,-70),(33,-57)).segment((45,-51)).segment((45,-49)).segment((43,-49)).segment((43,-41)).segment((29,-20)).segment((26,-22)).segment((21,-14)).segment((11,-20)).segment((11,-21)).segment((-10,-10)).segment((-42,-37)).segment((-36,-45)).segment((-33,-43)).segment((-30,-51)).close().assemble().reset().face(w0.sketch().segment((-23,80),(-11,57)).segment((23,72)).segment((11,95)).segment((10,95)).arc((-13,95),(-22,79)).close().assemble()).push([(0,83)]).circle(11,mode='s').finalize().extrude(46))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0060_00603582.step')
