import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-14))
r=w0.sketch().push([(-85.5,0)]).rect(29,28).push([(-28.5,0)]).rect(29,28).push([(28.5,0)]).rect(29,28).push([(85.5,0)]).rect(29,28).finalize().extrude(28)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0088_00884632.step')
