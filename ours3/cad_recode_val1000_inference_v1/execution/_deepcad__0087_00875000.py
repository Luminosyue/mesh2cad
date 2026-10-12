import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().arc((-4,-2),(4,-2),(-3,0)).segment((-2,0)).segment((-2,-2)).close().assemble().finalize().extrude(193).union(w0.sketch().segment((-4,0),(-2,0)).segment((-2,-2)).segment((2,-2)).segment((2,2)).segment((-2,2)).segment((-2,1)).segment((-4,1)).arc((4,-2),(-4,0)).assemble().finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0087_00875000.step')
