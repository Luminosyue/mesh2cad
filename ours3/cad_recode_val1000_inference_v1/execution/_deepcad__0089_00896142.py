import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,4,0))
r=w0.sketch().segment((-100,6),(-91,6)).segment((-91,-20)).segment((-81,-20)).arc((-73,-36),(-63,-48)).segment((-6,-48)).segment((-6,-38)).segment((26,-38)).segment((26,-48)).segment((98,-48)).arc((95,-36),(89,-25)).segment((100,-25)).segment((100,38)).segment((80,38)).segment((80,48)).segment((60,48)).arc((48,34),(31,25)).segment((31,15)).segment((26,15)).segment((26,48)).segment((-18,48)).segment((-18,36)).arc((-22,36),(-26,35)).segment((-26,26)).segment((-47,26)).segment((-47,48)).segment((-84,48)).segment((-84,37)).segment((-96,37)).segment((-96,26)).segment((-100,26)).close().assemble().push([(-74,-24)]).circle(5,mode='s').push([(-50,-10)]).circle(13,mode='s').push([(63,-7)]).circle(17,mode='s').finalize().extrude(-8).union(w0.sketch().push([(-93,-42)]).circle(6).push([(63,-7)]).circle(23).finalize().extrude(-8))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0089_00896142.step')
