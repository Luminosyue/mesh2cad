import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-4))
r=w0.sketch().segment((-83,-35),(-29,-35)).segment((-29,-100)).segment((-26,-100)).segment((-26,-35)).segment((29,-35)).segment((29,-33)).segment((-26,-33)).segment((-26,33)).segment((-29,33)).segment((-29,-33)).segment((-83,-33)).close().assemble().push([(-27.5,98.5)]).rect(105,3).push([(82,-31)]).rect(4,132).finalize().extrude(8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0089_00897252.step')
