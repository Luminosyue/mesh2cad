import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(64,0,0))
r=w0.sketch().segment((-100,-64),(-17,-64)).segment((-17,-39)).segment((-13,-39)).segment((-13,-64)).segment((100,-64)).segment((100,64)).segment((-100,64)).close().assemble().push([(-60,-62)]).circle(3,mode='s').push([(41,17)]).circle(18,mode='s').finalize().extrude(-128).union(w0.sketch().segment((-96,-64),(96,-64)).segment((96,64)).segment((-96,64)).segment((-96,43)).arc((-54,17),(-96,-9)).close().assemble().finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0071_00714650.step')
