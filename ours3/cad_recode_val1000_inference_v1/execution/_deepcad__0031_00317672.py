import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,29,0))
r=w0.sketch().segment((-72,-100),(-1,-100)).segment((-1,-43)).segment((31,-43)).segment((31,-33)).segment((-1,-33)).segment((-1,15)).segment((14,15)).segment((14,-10)).segment((72,-10)).segment((72,28)).segment((65,28)).segment((65,49)).segment((52,49)).segment((52,67)).segment((47,67)).segment((47,76)).segment((28,76)).segment((28,93)).segment((-1,93)).segment((-1,100)).segment((-72,100)).close().assemble().reset().face(w0.sketch().segment((-71,-68),(-14,-88)).segment((-8,-68)).segment((-10,-68)).segment((-10,-61)).segment((-7,-61)).segment((-7,-68)).segment((-6,-61)).segment((-71,-31)).close().assemble()).finalize().extrude(-58).union(w0.sketch().segment((-72,-100),(14,-100)).segment((14,-43)).segment((71,-43)).segment((71,28)).segment((41,28)).segment((41,-33)).segment((-72,-33)).close().assemble().finalize().extrude(-44))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0031_00317672.step')
