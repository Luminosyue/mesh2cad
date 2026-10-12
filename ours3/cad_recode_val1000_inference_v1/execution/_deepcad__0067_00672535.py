import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,13,0))
r=w0.sketch().segment((-26,-100),(25,-100)).segment((25,-90)).segment((26,-90)).segment((25,-41)).segment((25,-24)).segment((23,-24)).segment((23,-23)).segment((25,-23)).segment((26,100)).segment((-25,100)).segment((-25,-15)).segment((-26,-15)).close().assemble().finalize().extrude(-26)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0067_00672535.step')
