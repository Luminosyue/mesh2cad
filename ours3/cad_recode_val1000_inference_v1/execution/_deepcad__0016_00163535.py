import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-70))
r=w0.sketch().segment((-87,-49),(-87,-29)).segment((-75,-29)).segment((-75,-67)).arc((-54,-78),(-31,-86)).segment((-31,-98)).segment((31,-98)).segment((31,-86)).arc((99,0),(31,86)).segment((31,98)).segment((-31,98)).segment((-31,86)).arc((-90,43),(-87,-49)).assemble().push([(-20,0)]).circle(43,mode='s').finalize().extrude(18).union(w0.sketch().segment((-75,-35),(-23,-86)).segment((-13,-77)).arc((73,65),(-75,-35)).assemble().reset().face(w0.sketch().segment((-56,64),(-13,-50)).segment((32,-33)).segment((-11,81)).close().assemble(),mode='s').finalize().extrude(81)).union(w0.sketch().arc((27,-13),(61,-36),(97,-13)).segment((93,-13)).arc((61,-32),(29,-13)).close().assemble().reset().face(w0.sketch().segment((27,13),(29,13)).arc((61,32),(93,13)).segment((97,13)).arc((61,36),(27,13)).assemble()).finalize().extrude(141))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0016_00163535.step')
