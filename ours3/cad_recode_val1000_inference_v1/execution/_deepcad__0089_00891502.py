import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().arc((19,23),(20,19),(20,15)).arc((24,-24),(60,-42)).segment((60,-28)).arc((26,-10),(24,26)).arc((22,25),(19,23)).assemble().reset().face(w0.sketch().arc((30,35),(73,33),(92,-7)).segment((100,-7)).arc((80,36),(30,35)).assemble()).reset().face(w0.sketch().arc((64,-42),(70,-40),(75,-38)).arc((69,-30),(64,-23)).close().assemble()).finalize().extrude(-10).union(w0.sketch().arc((-92,-34),(-54,-72),(-1,-76)).segment((-14,-65)).arc((-47,-65),(-74,-47)).segment((-90,-39)).segment((-46,48)).segment((-1,26)).arc((22,15),(38,-5)).segment((54,-13)).segment((28,-62)).arc((38,-52),(45,-40)).segment((59,-42)).arc((54,-24),(47,-7)).arc((-15,79),(-92,3)).arc((-100,-15),(-92,-34)).assemble().reset().face(w0.sketch().arc((-14,-78),(-1,-76),(11,-72)).close().assemble()).finalize().extrude(14))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0089_00891502.step')
