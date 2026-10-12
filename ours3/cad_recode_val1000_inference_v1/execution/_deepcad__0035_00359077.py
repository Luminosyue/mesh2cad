import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-98,-22),(-98,22)).arc((-100,0),(-98,-22)).assemble().reset().face(w0.sketch().arc((-95,-32),(-87,-49),(-75,-66)).segment((-75,-67)).segment((-74,-67)).arc((-65,-76),(-55,-84)).segment((-55,-85)).segment((-54,-85)).arc((-10,-100),(34,-93)).segment((35,-93)).segment((35,-92)).arc((42,-89),(49,-85)).segment((50,-85)).segment((50,-84)).arc((61,-79),(70,-71)).segment((-10,-90)).segment((-24,-32)).close().assemble()).reset().face(w0.sketch().segment((-95,32),(-75,32)).segment((-75,49)).segment((74,72)).arc((15,96),(-48,88)).segment((-49,88)).segment((-49,87)).arc((-69,72),(-86,52)).segment((-87,52)).segment((-87,51)).arc((-91,43),(-95,32)).assemble()).reset().face(w0.sketch().segment((-44,-52),(83,-52)).segment((83,-58)).arc((35,93),(-44,-48)).close().assemble()).finalize().extrude(-25).union(w0.sketch().push([(0,62)]).circle(24).circle(19,mode='s').finalize().extrude(25))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0035_00359077.step')
