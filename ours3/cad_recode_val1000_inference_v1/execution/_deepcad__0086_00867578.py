import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,0,0))
r=w0.sketch().segment((-32,-92),(-26,-93)).segment((-26,-54)).segment((-13,-54)).segment((-13,-81)).segment((-11,-82)).segment((-10,-77)).segment((5,-70)).segment((5,-50)).segment((28,-50)).segment((28,-51)).segment((32,-21)).arc((24,-1),(32,19)).segment((32,20)).segment((19,20)).segment((32,38)).segment((28,41)).segment((28,54)).segment((17,54)).segment((7,67)).segment((7,69)).segment((5,69)).segment((-27,100)).segment((-32,92)).segment((-26,89)).segment((-26,54)).segment((-29,54)).segment((-29,55)).segment((-32,4)).segment((-29,2)).segment((-29,-17)).segment((-26,-17)).segment((-26,-38)).close().assemble().finalize().extrude(-0)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0086_00867578.step')
