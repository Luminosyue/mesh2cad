import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('XY',origin=(0,0,-8))
r=w0.sketch().segment((-84,55),(-83,-61)).segment((-37,-60)).arc((-59,-10),(-44,35)).arc((-62,47),(-50,60)).close().assemble().reset().face(w0.sketch().segment((-4,-59),(84,-58)).segment((83,58)).segment((-4,59)).arc((25,0),(-4,-59)).assemble()).finalize().extrude(200).union(w1.sketch().arc((-59,32),(-50,26),(-43,19)).segment((-43,-83)).segment((54,-83)).segment((54,19)).arc((58,24),(61,30)).segment((54,30)).segment((54,32)).segment((59,32)).arc((58,43),(54,54)).segment((54,56)).segment((-43,56)).segment((-43,54)).arc((-47,47),(-50,39)).arc((-51,35),(-54,32)).close().assemble().finalize().extrude(90))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0038_00383797.step')
