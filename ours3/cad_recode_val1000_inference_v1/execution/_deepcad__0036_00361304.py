import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,17,0))
r=w0.sketch().segment((-46,-100),(38,-100)).segment((38,6)).segment((37,6)).segment((37,33)).segment((-46,33)).segment((-46,6)).close().assemble().reset().face(w0.sketch().segment((-46,-91),(-45,-91)).arc((-43,-92),(-41,-91)).segment((-40,-91)).segment((-40,-89)).segment((-41,-89)).arc((-43,-88),(-45,-89)).segment((-46,-89)).close().assemble(),mode='s').push([(-4,-96)]).circle(4,mode='s').finalize().extrude(-84).union(w0.sketch().push([(-3,-50)]).rect(86,98).push([(35,-7)]).circle(5,mode='s').finalize().extrude(-48)).union(w0.sketch().segment((-2,100),(45,50)).segment((46,51)).segment((46,100)).close().assemble().finalize().extrude(50))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0036_00361304.step')
