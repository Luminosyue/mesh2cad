import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,5))
w1=cq.Workplane('ZX',origin=(0,57,0))
r=w0.sketch().push([(-30.5,-4.5)]).rect(17,17).push([(91,-4.5)]).rect(18,17).finalize().extrude(-35).union(w0.workplane(offset=-29/2).moveTo(-30.5,48).box(17,18,29)).union(w0.sketch().segment((-100,-57),(-53,-57)).segment((-80,-17)).segment((-47,4)).segment((-47,13)).segment((-100,13)).close().assemble().reset().face(w0.sketch().segment((-44,-57),(39,-57)).segment((39,13)).segment((-14,13)).segment((13,-27)).close().assemble()).finalize().extrude(26)).union(w1.sketch().segment((-31,83),(-1,83)).arc((0,84),(1,83)).segment((4,83)).segment((4,100)).segment((-31,100)).close().assemble().finalize().extrude(-18))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0014_00148597.step')
