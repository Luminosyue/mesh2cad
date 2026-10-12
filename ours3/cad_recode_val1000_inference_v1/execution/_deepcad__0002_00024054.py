import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-43))
w1=cq.Workplane('YZ',origin=(11,0,0))
r=w0.sketch().segment((-30,-17),(-19,-17)).arc((-10,-19),(-1,-17)).segment((19,-17)).segment((19,100)).segment((-19,100)).segment((-19,56)).segment((-30,56)).close().assemble().push([(14,41)]).circle(10,mode='s').finalize().extrude(24).union(w0.sketch().segment((-9,-94),(30,-94)).segment((30,-23)).segment((10,-23)).arc((10,-58),(-9,-87)).close().assemble().finalize().extrude(24)).union(w1.sketch().segment((-100,-32),(-93,-32)).segment((-93,-43)).segment((-31,-43)).segment((-31,-32)).segment((-24,-32)).segment((-24,-19)).segment((-31,-19)).segment((-31,43)).segment((-100,43)).close().assemble().push([(-62,15)]).circle(15,mode='s').push([(63,8.5)]).rect(64,69).finalize().extrude(-41))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00024054.step')
