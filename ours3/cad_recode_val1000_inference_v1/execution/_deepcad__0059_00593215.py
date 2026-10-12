import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,25,0))
w1=cq.Workplane('YZ',origin=(87,0,0))
r=w0.sketch().segment((-17,-100),(17,-100)).segment((17,-49)).arc((13,-50),(9,-49)).segment((9,-59)).segment((7,-59)).segment((7,-82)).segment((-7,-82)).segment((-7,-59)).segment((-9,-59)).segment((-9,-49)).segment((-17,-49)).close().assemble().reset().face(w0.sketch().arc((-17,-19),(0,34),(17,-19)).segment((17,32)).segment((-17,32)).close().assemble()).reset().face(w0.sketch().segment((-17,62),(-16,61)).segment((17,75)).segment((17,100)).segment((0,100)).segment((0,90)).segment((-1,91)).segment((-17,73)).close().assemble()).finalize().extrude(-50).union(w0.sketch().segment((-10,-36),(10,-36)).segment((10,-22)).arc((0,-23),(-10,-22)).close().assemble().finalize().extrude(-31)).union(w1.sketch().arc((-15,-17),(-11,-16),(-7,-14)).arc((-9,-10),(-8,-5)).arc((-12,-4),(-15,-1)).close().assemble().finalize().extrude(-187))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0059_00593215.step')
