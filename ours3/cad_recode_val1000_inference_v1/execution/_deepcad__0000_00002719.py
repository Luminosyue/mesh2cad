import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(49,0,0))
w1=cq.Workplane('ZX',origin=(0,35,0))
r=w0.sketch().segment((-53,-56),(-20,-56)).segment((-20,-100)).segment((40,-100)).segment((40,-56)).segment((53,-56)).segment((53,100)).segment((-53,100)).segment((-53,51)).arc((-44,61),(-32,68)).segment((-32,82)).segment((32,82)).segment((32,68)).arc((44,61),(53,51)).segment((53,52)).segment((40,52)).segment((40,63)).segment((-20,63)).segment((-20,52)).segment((-53,52)).close().assemble().reset().face(w0.sketch().arc((-12,-56),(0,-57),(12,-56)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-12,52),(12,52)).arc((0,54),(-12,52)).assemble(),mode='s').finalize().extrude(-116).union(w0.sketch().segment((-53,-82),(-20,-100)).segment((23,-13)).segment((-10,5)).close().assemble().push([(0,49)]).rect(94,26).finalize().extrude(18)).union(w1.sketch().segment((-100,-49),(-92,-49)).segment((-92,-67)).segment((92,-67)).segment((92,-49)).segment((100,-49)).segment((100,67)).segment((92,67)).segment((92,49)).segment((-92,49)).segment((-92,67)).segment((-100,67)).close().assemble().finalize().extrude(18))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0000_00002719.step')
