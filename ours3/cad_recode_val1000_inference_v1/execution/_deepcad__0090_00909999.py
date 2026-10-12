import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-7,-95),(-6,-95)).segment((-6,-24)).arc((7,-14),(-6,-4)).segment((-6,64)).arc((0,61),(6,57)).segment((6,-4)).arc((7,-4),(7,-3)).segment((7,57)).arc((0,61),(6,64)).segment((6,97)).arc((0,99),(-6,100)).segment((-6,64)).arc((-8,59),(-6,54)).segment((-6,-3)).arc((-7,-4),(-7,-5)).segment((-6,-5)).segment((-6,-95)).segment((7,-95)).segment((7,-100)).segment((6,-100)).segment((6,-100)).segment((-6,-100)).segment((-6,-100)).segment((-7,-100)).close().assemble().finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0090_00909999.step')
