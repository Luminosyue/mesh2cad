import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,20))
w1=cq.Workplane('ZX',origin=(0,-7,0))
r=w0.sketch().segment((-25,-7),(-16,-7)).segment((-16,0)).arc((-18,1),(-16,2)).segment((-16,24)).segment((-25,24)).close().assemble().finalize().extrude(-43).union(w0.sketch().segment((-83,8),(-29,8)).segment((-29,9)).segment((42,9)).segment((42,48)).segment((-29,48)).segment((-29,48)).segment((-83,48)).close().assemble().push([(20,28)]).circle(2,mode='s').finalize().extrude(-11)).union(w0.sketch().segment((-100,-37),(-95,-37)).segment((-95,-48)).segment((-80,-48)).segment((-80,-37)).segment((-75,-37)).segment((-75,-22)).segment((-80,-22)).segment((-80,-19)).segment((-95,-19)).segment((-95,-22)).segment((-100,-22)).close().assemble().push([(-89,6)]).circle(6).reset().face(w0.sketch().segment((-56,-33),(33,-49)).segment((42,-6)).segment((-47,11)).close().assemble()).finalize().extrude(3)).union(w1.sketch().arc((-19,92),(-12,92),(-6,91)).arc((-1,92),(2,97)).arc((1,98),(0,100)).arc((-13,99),(-19,92)).assemble().finalize().extrude(40))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0080_00808287.step')
