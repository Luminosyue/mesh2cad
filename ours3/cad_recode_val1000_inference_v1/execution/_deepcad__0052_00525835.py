import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-26,-92),(-18,-92)).segment((-19,-95)).segment((25,-100)).segment((26,-92)).segment((26,-59)).segment((23,-59)).segment((26,-51)).segment((19,-49)).segment((26,-24)).segment((26,3)).segment((18,3)).segment((19,13)).segment((-3,13)).segment((-3,27)).segment((16,27)).segment((26,75)).segment((26,100)).segment((-18,100)).segment((-18,87)).segment((-26,87)).segment((-26,37)).segment((-26,3)).segment((-26,-13)).segment((-23,-13)).segment((-26,-38)).segment((-26,-61)).segment((-23,-61)).segment((-26,-70)).close().assemble().finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0052_00525835.step')
