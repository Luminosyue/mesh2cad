import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(6,0,0))
r=w0.sketch().segment((-65,-100),(-27,-100)).segment((-27,-80)).segment((5,-80)).segment((5,-100)).segment((65,-100)).segment((65,-52)).segment((43,-52)).segment((43,-34)).segment((65,-34)).segment((65,100)).segment((-65,100)).segment((-65,82)).segment((-60,95)).segment((-10,71)).segment((-10,100)).segment((-57,100)).segment((-57,52)).segment((-65,61)).segment((-65,-42)).segment((-13,-42)).segment((-13,-62)).segment((-65,-62)).close().assemble().reset().face(w0.sketch().segment((-39,34),(-13,-14)).segment((-13,34)).segment((23,34)).segment((14,52)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-10,-34),(10,-34)).segment((10,-14)).segment((-10,-14)).segment((-10,-15)).close().assemble(),mode='s').push([(48,-74)]).rect(34,36).push([(48,74)]).rect(34,36).finalize().extrude(-12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0017_00176265.step')
