import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().arc((-95,-31),(-86,-51),(-72,-69)).segment((-72,-70)).segment((-71,-70)).arc((-60,-79),(-46,-89)).arc((-47,-87),(-47,-85)).arc((-60,-77),(-70,-66)).arc((-13,1),(-29,-75)).arc((-19,-81),(-10,-89)).segment((-10,-99)).segment((10,-99)).segment((10,-98)).arc((78,-63),(95,12)).segment((95,13)).arc((86,51),(60,79)).segment((60,77)).arc((13,80),(-29,54)).segment((-29,95)).arc((-50,87),(-69,74)).segment((-69,70)).arc((-97,24),(-95,-31)).assemble().reset().face(w0.sketch().arc((-10,54),(6,49),(20,40)).segment((20,54)).close().assemble(),mode='s').reset().face(w0.sketch().arc((29,-95),(83,-53),(95,12)).segment((95,13)).segment((29,13)).close().assemble()).finalize().extrude(-42).union(w0.sketch().segment((35,-94),(100,-94)).segment((100,-36)).arc((67,-58),(35,-36)).close().assemble().reset().face(w0.sketch().arc((35,-7),(67,15),(100,-7)).segment((100,0)).segment((35,0)).close().assemble()).finalize().extrude(43))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0076_00763822.step')
