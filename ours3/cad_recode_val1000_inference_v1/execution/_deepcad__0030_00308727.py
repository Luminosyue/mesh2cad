import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,7,0))
r=w0.sketch().segment((-100,-100),(-83,-100)).segment((-83,-51)).segment((-64,-51)).segment((-64,-77)).segment((-47,-77)).segment((-47,-87)).segment((-34,-87)).segment((-34,-100)).segment((18,-100)).segment((18,-87)).segment((100,-87)).segment((100,100)).segment((43,100)).segment((99,69)).segment((58,-10)).segment((58,-38)).segment((42,-38)).segment((42,-11)).segment((18,-51)).segment((18,-42)).segment((-24,-42)).segment((42,27)).segment((42,55)).segment((58,55)).segment((58,30)).segment((100,69)).segment((100,100)).segment((-100,100)).segment((-100,42)).segment((-100,41)).close().assemble().reset().face(w0.sketch().segment((-98,41),(-83,13)).segment((-83,41)).close().assemble()).reset().face(w0.sketch().segment((-79,-26),(-64,-26)).segment((-64,6)).close().assemble()).reset().face(w0.sketch().segment((-59,27),(-47,27)).segment((-47,41)).close().assemble()).finalize().extrude(-14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00308727.step')
