import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('YZ',origin=(66,0,0))
r=w0.sketch().arc((-99,-10),(-95,-29),(-90,-46)).arc((-30,-43),(-74,-66)).arc((19,-98),(95,-31)).segment((95,-28)).segment((96,-28)).arc((99,-10),(99,9)).arc((97,17),(95,25)).segment((95,31)).segment((94,31)).arc((76,64),(46,89)).arc((34,57),(24,89)).arc((-55,82),(-94,13)).arc((-99,3),(-99,-10)).assemble().finalize().extrude(-199).union(w1.sketch().arc((-89,45),(-99,-10),(-73,-61)).segment((-73,-70)).segment((-64,-70)).arc((0,-96),(64,-70)).segment((73,-70)).segment((73,-61)).arc((99,0),(73,61)).segment((73,70)).segment((64,70)).arc((0,96),(-64,70)).segment((-73,70)).segment((-73,61)).arc((-80,55),(-85,49)).segment((-85,45)).close().assemble().finalize().extrude(-166))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0045_00458645.step')
