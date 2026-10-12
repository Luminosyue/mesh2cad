import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-80,0))
r=w0.sketch().segment((-93,-79),(-5,-79)).segment((-5,-80)).segment((5,-80)).segment((5,-79)).segment((93,-79)).segment((93,79)).segment((5,79)).segment((5,80)).segment((-5,80)).segment((-5,79)).segment((-93,79)).close().assemble().finalize().extrude(40).union(w0.sketch().segment((-100,-80),(-5,-80)).segment((-5,-79)).arc((-27,-75),(-47,-64)).segment((47,-64)).arc((27,-75),(5,-79)).segment((5,-80)).segment((64,-80)).segment((64,80)).segment((5,80)).segment((-5,80)).segment((-100,80)).close().assemble().reset().face(w0.sketch().arc((81,-73),(91,-69),(100,-64)).segment((100,80)).segment((81,80)).close().assemble()).finalize().extrude(160)).union(w0.sketch().arc((-10,25),(20,-11),(12,-57)).segment((100,-57)).segment((100,73)).segment((-10,73)).close().assemble().finalize().extrude(160))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0035_00353610.step')
