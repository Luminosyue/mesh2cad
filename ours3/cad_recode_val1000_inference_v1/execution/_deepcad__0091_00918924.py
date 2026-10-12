import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-28))
r=w0.sketch().segment((-50,-96),(50,-96)).segment((50,96)).segment((-17,96)).arc((-23,63),(-50,38)).segment((-50,-10)).arc((10,-38),(-50,-64)).close().assemble().finalize().extrude(24).union(w0.sketch().segment((-50,-96),(-42,-96)).segment((-42,-100)).segment((47,-100)).segment((47,-96)).segment((50,-96)).segment((50,96)).segment((47,96)).segment((47,100)).segment((-42,100)).segment((-42,96)).segment((-50,96)).close().assemble().finalize().extrude(56))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0091_00918924.step')
