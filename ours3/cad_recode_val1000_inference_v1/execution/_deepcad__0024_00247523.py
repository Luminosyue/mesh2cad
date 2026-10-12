import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(2,0,0))
r=w0.sketch().segment((-100,-35),(98,-35)).segment((98,-16)).segment((100,-16)).segment((100,30)).segment((98,30)).segment((98,35)).segment((-97,35)).segment((-97,27)).segment((-91,27)).segment((-91,32)).segment((-47,32)).segment((-47,27)).segment((94,27)).segment((94,2)).segment((-47,2)).segment((-47,-6)).segment((-91,-6)).segment((-91,2)).segment((-100,2)).close().assemble().reset().face(w0.sketch().segment((-93,-28),(-15,-28)).segment((-15,-32)).segment((-13,-32)).segment((-13,-28)).segment((70,-28)).segment((70,-8)).segment((28,-8)).segment((28,2)).segment((-13,2)).segment((-13,6)).segment((-15,6)).segment((-15,2)).segment((-47,2)).segment((-47,-6)).segment((-93,-6)).close().assemble(),mode='s').push([(-16,0)]).circle(4).finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0024_00247523.step')
