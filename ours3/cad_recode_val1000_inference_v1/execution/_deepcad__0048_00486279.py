import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-18))
w1=cq.Workplane('XY',origin=(0,0,-8))
r=w0.sketch().segment((-100,-77),(-28,-77)).segment((-28,-42)).segment((-100,-43)).close().assemble().reset().face(w0.sketch().segment((-19,6),(2,-27)).arc((28,-39),(4,-54)).segment((38,-86)).segment((80,-42)).segment((75,-37)).segment((97,-37)).segment((96,15)).segment((79,15)).segment((79,5)).segment((63,27)).arc((89,79),(42,46)).close().assemble()).finalize().extrude(36).union(w1.sketch().arc((-100,-42),(-64,-62),(-28,-42)).close().assemble().reset().face(w1.sketch().segment((-20,-53),(22,-53)).segment((22,-72)).segment((23,-72)).segment((23,-53)).segment((65,-53)).segment((65,-18)).segment((23,-18)).segment((23,1)).segment((22,1)).segment((22,-18)).segment((-20,-18)).close().assemble()).finalize().extrude(26))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0048_00486279.step')
