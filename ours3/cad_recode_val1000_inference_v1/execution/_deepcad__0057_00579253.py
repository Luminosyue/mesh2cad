import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(50,0,0))
r=w0.sketch().segment((-75,-100),(75,-100)).segment((75,100)).segment((-75,100)).segment((-75,10)).segment((-46,10)).segment((-46,-10)).segment((-75,-10)).close().assemble().push([(17,-75)]).circle(15,mode='s').reset().face(w0.sketch().segment((34,74),(38,74)).segment((38,75)).arc((40,78),(38,81)).segment((38,82)).segment((34,82)).segment((34,81)).arc((32,78),(34,75)).close().assemble(),mode='s').reset().face(w0.sketch().segment((53,-81),(75,-81)).segment((75,-10)).segment((53,-10)).segment((53,-75)).segment((54,-75)).segment((54,-77)).segment((53,-77)).close().assemble()).finalize().extrude(-100).union(w0.sketch().arc((-75,-75),(36,0),(-75,75)).close().assemble().finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0057_00579253.step')
