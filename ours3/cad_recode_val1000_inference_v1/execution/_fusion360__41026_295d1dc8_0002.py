import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-8,0))
r=w0.sketch().segment((-100,-4),(-96,-4)).segment((-96,-8)).segment((-56,-8)).segment((-56,-4)).segment((-52,-4)).segment((-52,4)).segment((-56,4)).segment((-56,8)).segment((-96,8)).segment((-96,4)).segment((-100,4)).close().assemble().reset().face(w0.sketch().segment((-44,-8),(52,-8)).arc((58,-10),(64,-8)).segment((98,-8)).segment((98,0)).segment((100,0)).segment((100,4)).segment((98,4)).segment((98,8)).segment((-44,8)).close().assemble()).finalize().extrude(16)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__41026_295d1dc8_0002.step')
