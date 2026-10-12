import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,3,0))
r=w0.sketch().segment((-100,-64),(31,-64)).segment((31,-63)).segment((-100,-61)).close().assemble().reset().face(w0.sketch().segment((-99,60),(30,60)).segment((30,62)).segment((-99,63)).close().assemble()).reset().face(w0.sketch().segment((-37,-63),(31,-63)).segment((31,-64)).segment((37,-64)).segment((37,-63)).segment((37,-62)).segment((37,-61)).segment((37,-60)).segment((37,-30)).segment((92,-31)).segment((92,-9)).segment((100,-9)).segment((100,62)).segment((98,62)).segment((98,-9)).segment((92,-9)).segment((92,-28)).segment((-34,-28)).segment((-34,29)).segment((80,29)).segment((80,32)).segment((-34,32)).segment((-34,40)).segment((-37,40)).segment((-37,-9)).segment((-34,-9)).segment((-34,-28)).segment((-37,-28)).close().assemble()).finalize().extrude(-6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0093_00933832.step')
