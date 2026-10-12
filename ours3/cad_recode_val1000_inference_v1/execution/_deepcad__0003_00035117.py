import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(17,0,0))
w1=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-83,-100),(50,-100)).segment((50,-24)).segment((41,-24)).segment((41,-14)).arc((-12,-22),(-48,20)).segment((-21,20)).segment((-21,33)).segment((-83,33)).close().assemble().reset().face(w0.sketch().arc((17,-66),(24,-58),(28,-48)).arc((23,-57),(17,-66)).assemble(),mode='s').reset().face(w0.sketch().arc((17,95),(59,59),(39,10)).arc((44,36),(37,61)).arc((73,83),(32,73)).arc((24,84),(17,95)).assemble()).finalize().extrude(-67).union(w0.workplane(offset=-56/2).moveTo(50,55).box(66,90,56)).union(w0.sketch().segment((-83,-100),(-64,-100)).segment((-64,-78)).arc((-74,-72),(-64,-66)).segment((-64,-49)).segment((-83,-49)).close().assemble().push([(13,-26)]).circle(37).finalize().extrude(-1)).union(w1.sketch().segment((-33,-15),(-17,-15)).segment((-17,-50)).segment((50,-50)).segment((50,17)).segment((21,17)).segment((21,16)).segment((-33,16)).close().assemble().finalize().extrude(67))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0003_00035117.step')
