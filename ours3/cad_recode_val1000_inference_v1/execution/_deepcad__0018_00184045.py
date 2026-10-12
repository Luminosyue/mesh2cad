import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(21,0,0))
r=w0.sketch().segment((-90,4),(-74,4)).segment((-74,-21)).segment((-29,-21)).segment((-29,4)).segment((-13,4)).segment((-13,21)).segment((-29,21)).segment((-29,29)).segment((-74,29)).segment((-74,21)).segment((-90,21)).close().assemble().push([(52,0)]).rect(82,44).finalize().extrude(-50).union(w0.sketch().segment((-100,-30),(-18,-30)).segment((-18,-21)).segment((-74,-21)).segment((-74,21)).segment((-100,21)).close().assemble().push([(52,0)]).rect(96,58).finalize().extrude(-30)).union(w0.sketch().push([(-45,0)]).circle(21).push([(52,0)]).rect(96,58).finalize().extrude(8))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0018_00184045.step')
