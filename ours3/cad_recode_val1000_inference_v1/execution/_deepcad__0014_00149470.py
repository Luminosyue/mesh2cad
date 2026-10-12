import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('YZ',origin=(58,0,0))
r=w0.sketch().segment((-44,-74),(-19,-91)).segment((-19,-100)).segment((58,-100)).segment((58,100)).segment((56,100)).segment((56,96)).segment((55,96)).segment((55,89)).segment((56,89)).segment((56,86)).segment((58,86)).segment((58,-59)).segment((-19,-10)).segment((-19,-33)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((3,1),(19,25)).segment((19,34)).segment((25,34)).segment((33,46)).arc((25,46),(19,44)).segment((19,26)).arc((11,16),(3,1)).assemble().finalize().extrude(-159)).union(w1.sketch().arc((-59,9),(-1,-10),(29,-61)).arc((40,-62),(51,-62)).arc((52,-72),(52,-82)).arc((86,-79),(85,-44)).arc((86,-34),(85,-24)).arc((10,61),(-59,9)).assemble().finalize().extrude(-15))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0014_00149470.step')
