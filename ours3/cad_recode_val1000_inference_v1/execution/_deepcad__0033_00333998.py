import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,59,0))
w1=cq.Workplane('ZX',origin=(0,38,0))
r=w0.sketch().arc((-95,-23),(-93,-35),(-88,-46)).close().assemble().reset().face(w0.sketch().segment((-95,25),(-62,77)).arc((-84,49),(-95,25)).assemble()).reset().face(w0.sketch().arc((-64,-43),(-59,-47),(-56,-53)).arc((-50,-58),(-44,-62)).close().assemble()).reset().face(w0.sketch().segment((-32,94),(23,88)).arc((0,100),(-32,94)).assemble()).reset().face(w0.sketch().arc((-21,-74),(0,-87),(21,-97)).segment((16,-74)).close().assemble()).reset().face(w0.sketch().arc((31,-94),(43,-89),(54,-82)).arc((99,-4),(59,79)).segment((76,10)).arc((71,-30),(43,-63)).close().assemble()).finalize().extrude(-119).union(w0.sketch().arc((-90,-42),(-76,-63),(-54,-76)).close().assemble().reset().face(w0.sketch().segment((-84,51),(53,77)).arc((-22,95),(-84,51)).assemble()).reset().face(w0.sketch().arc((51,-84),(73,-56),(84,-22)).close().assemble()).finalize().extrude(-118)).union(w1.workplane(offset=-43/2).moveTo(-21,-74).cylinder(43,5))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0033_00333998.step')
