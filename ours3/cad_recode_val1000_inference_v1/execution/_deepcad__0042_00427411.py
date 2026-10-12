import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(17,0,0))
r=w0.sketch().segment((-25,-100),(25,-100)).segment((25,-14)).arc((20,-16),(15,-17)).segment((15,-20)).segment((12,-20)).segment((12,-17)).arc((-10,0),(12,17)).segment((12,20)).segment((15,20)).segment((15,17)).arc((20,16),(25,14)).segment((25,100)).segment((-25,100)).close().assemble().finalize().extrude(-34).union(w0.sketch().segment((-25,13),(23,13)).arc((20,37),(25,60)).segment((25,96)).segment((-25,96)).close().assemble().finalize().extrude(-28))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00427411.step')
