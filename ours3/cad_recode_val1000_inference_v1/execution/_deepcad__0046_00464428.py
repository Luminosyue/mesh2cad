import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,60,0))
r=w0.sketch().segment((-70,-100),(70,-100)).segment((70,97)).arc((34,99),(5,100)).segment((-70,100)).segment((-70,49)).segment((-70,-24)).close().assemble().push([(0,-85)]).rect(14,28,mode='s').push([(0,26)]).rect(14,28,mode='s').finalize().extrude(-120).union(w0.sketch().segment((-70,-35),(-4,-35)).segment((-4,-100)).segment((4,-100)).segment((4,-35)).segment((70,-35)).segment((70,100)).segment((-70,100)).close().assemble().finalize().extrude(-115))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0046_00464428.step')
