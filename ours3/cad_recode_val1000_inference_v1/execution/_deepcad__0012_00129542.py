import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().push([(-86,-28)]).circle(14).push([(-86.5,-28)]).rect(1,12,mode='s').reset().face(w0.sketch().segment((-97,35),(-88,27)).segment((-84,32)).arc((-77,35),(-75,42)).segment((-74,44)).segment((-84,51)).segment((-86,47)).arc((-96,45),(-96,37)).close().assemble()).push([(-86,39)]).circle(4,mode='s').reset().face(w0.sketch().segment((-72,-3),(-69,-7)).segment((-63,-7)).segment((-69,-2)).close().assemble()).reset().face(w0.sketch().arc((14,-4),(-10,-38),(31,-30)).arc((27,-16),(14,-4)).assemble()).push([(8,-28)]).circle(4,mode='s').push([(86,-28)]).circle(14).circle(4,mode='s').finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0012_00129542.step')
