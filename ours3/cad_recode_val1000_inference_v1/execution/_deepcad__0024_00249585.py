import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,7))
r=w0.sketch().segment((-100,-62),(-93,-62)).segment((-93,-91)).segment((-24,-91)).segment((-88,44)).segment((-12,79)).segment((-12,80)).segment((-10,80)).segment((19,91)).arc((-32,90),(-75,91)).segment((-93,82)).segment((-93,70)).arc((-97,53),(-98,36)).segment((-100,36)).close().assemble().reset().face(w0.sketch().segment((-70,-36),(-12,-63)).segment((-12,-26)).segment((-26,-26)).segment((-26,26)).segment((-12,26)).segment((-12,36)).segment((-57,36)).arc((-58,15),(-70,-3)).close().assemble()).reset().face(w0.sketch().segment((-10,-70),(46,-91)).segment((100,-91)).segment((100,70)).segment((86,70)).segment((93,82)).segment((66,91)).segment((24,43)).segment((56,43)).segment((56,-26)).segment((12,-26)).close().assemble()).finalize().extrude(-14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0024_00249585.step')
