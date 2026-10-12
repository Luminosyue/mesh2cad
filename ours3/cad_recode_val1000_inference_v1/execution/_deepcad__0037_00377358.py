import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-6))
r=w0.sketch().segment((-100,19),(-92,19)).segment((-92,6)).segment((-85,6)).arc((-78,-33),(-46,-58)).segment((-61,-78)).segment((-38,-93)).segment((-21,-70)).arc((-1,-82),(20,-93)).segment((20,-92)).arc((-8,-64),(-14,-25)).segment((10,-25)).arc((1,-14),(-10,-6)).segment((10,19)).segment((19,19)).segment((19,27)).segment((38,27)).segment((38,40)).segment((-10,28)).arc((-17,57),(-46,72)).segment((-31,86)).segment((-14,67)).segment((-14,93)).segment((-92,93)).segment((-92,83)).segment((-100,83)).close().assemble().reset().face(w0.sketch().segment((23,-41),(59,-91)).segment((67,-61)).segment((67,-53)).segment((69,-53)).segment((92,-1)).segment((56,16)).close().assemble()).reset().face(w0.sketch().segment((38,38),(99,18)).segment((100,19)).segment((100,93)).segment((38,93)).close().assemble()).finalize().extrude(12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0037_00377358.step')
