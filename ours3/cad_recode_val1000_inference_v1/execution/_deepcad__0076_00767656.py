import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,32))
w1=cq.Workplane('YZ',origin=(18,0,0))
r=w0.sketch().segment((-12,-41),(-12,-28)).arc((-15,0),(-8,28)).arc((-18,0),(-12,-28)).segment((-12,-33)).arc((-13,-37),(-12,-41)).assemble().reset().face(w0.sketch().segment((-10,42),(-8,42)).arc((-4,54),(3,65)).arc((-4,54),(-10,42)).assemble()).reset().face(w0.sketch().arc((-7,-57),(1,-72),(12,-83)).segment((7,-98)).segment((10,-100)).segment((15,-85)).arc((17,-85),(18,-84)).segment((16,-84)).segment((19,-78)).segment((16,-77)).arc((16,-76),(17,-75)).arc((18,-53),(-7,-57)).assemble()).finalize().extrude(-64).union(w0.sketch().segment((-5,61),(0,59)).segment((15,95)).segment((8,100)).close().assemble().finalize().extrude(-60)).union(w1.sketch().arc((-37,24),(-93,-10),(-27,-10)).arc((-1,-31),(32,-25)).arc((56,-28),(76,-13)).segment((66,-13)).arc((50,-26),(32,-13)).segment((13,-13)).segment((13,29)).arc((12,28),(11,28)).segment((11,32)).arc((-13,18),(-37,24)).assemble().finalize().extrude(1))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0076_00767656.step')
