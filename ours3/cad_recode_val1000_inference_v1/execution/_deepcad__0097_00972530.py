import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-40))
w1=cq.Workplane('YZ',origin=(-35,0,0))
r=w0.sketch().segment((-100,-59),(-84,-59)).segment((-84,-73)).segment((-66,-73)).segment((-66,-59)).segment((-50,-59)).segment((-50,-45)).segment((-17,-67)).segment((-17,-66)).segment((4,-66)).segment((29,-52)).segment((29,-12)).segment((17,-12)).segment((17,24)).segment((-20,24)).segment((-20,-12)).segment((-28,-12)).segment((-28,-7)).segment((-10,24)).segment((-42,24)).segment((-42,53)).segment((-38,53)).segment((-40,55)).segment((-81,21)).segment((-53,-12)).segment((-66,-12)).segment((-66,1)).segment((-84,1)).segment((-84,-12)).segment((-100,-12)).close().assemble().finalize().extrude(6).union(w0.workplane(offset=65/2).moveTo(40,-27.5).box(102,7,65)).union(w0.sketch().arc((93,-31),(100,21),(93,73)).close().assemble().finalize().extrude(80)).union(w1.sketch().segment((-31,-34),(73,-34)).segment((73,35)).segment((68,35)).segment((68,38)).segment((25,38)).segment((25,35)).segment((-31,35)).close().assemble().push([(31,2)]).circle(22,mode='s').finalize().extrude(-7))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00972530.step')
