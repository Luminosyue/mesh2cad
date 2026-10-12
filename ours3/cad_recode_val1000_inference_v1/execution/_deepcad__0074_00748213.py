import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,30,0))
r=w0.sketch().segment((-58,36),(19,36)).segment((19,79)).segment((-58,79)).segment((-58,54)).arc((-56,53),(-58,52)).close().assemble().finalize().extrude(-85).union(w0.sketch().segment((-58,59),(-40,59)).segment((-40,37)).segment((19,37)).segment((19,59)).segment((37,59)).segment((37,78)).segment((19,78)).segment((19,100)).segment((-40,100)).segment((-40,78)).segment((-58,78)).close().assemble().finalize().extrude(-72)).union(w0.sketch().segment((-19,-62),(-10,-62)).segment((-14,-78)).segment((27,-97)).segment((34,-81)).segment((27,-81)).segment((27,-62)).segment((58,-62)).segment((58,-22)).segment((51,-22)).segment((51,-42)).segment((36,-42)).segment((36,-61)).segment((-19,-61)).close().assemble().push([(19,24)]).rect(78,152).finalize().extrude(25))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00748213.step')
