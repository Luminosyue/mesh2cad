import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-67))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,100)).segment((-91,100)).arc((-90,63),(-100,27)).close().assemble().push([(31,26)]).circle(51,mode='s').finalize().extrude(67).union(w0.sketch().segment((-100,-57),(-33,-57)).segment((-33,-100)).segment((33,-100)).segment((33,-57)).segment((100,-57)).segment((100,10)).segment((33,10)).segment((33,100)).segment((-33,100)).segment((-33,39)).segment((-100,39)).close().assemble().reset().face(w0.sketch().segment((-33,-39),(-33,-24)).arc((-40,-32),(-33,-39)).assemble(),mode='s').reset().face(w0.sketch().arc((-33,-39),(-26,-32),(-33,-24)).close().assemble(),mode='s').finalize().extrude(67)).union(w0.sketch().segment((-34,-100),(34,-100)).segment((34,-65)).arc((0,-66),(-34,-55)).close().assemble().reset().face(w0.sketch().arc((-34,65),(0,76),(34,74)).segment((34,100)).segment((-34,100)).close().assemble()).finalize().extrude(134))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00685679.step')
