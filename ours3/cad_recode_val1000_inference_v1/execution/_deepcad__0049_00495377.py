import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,4))
r=w0.sketch().segment((-56,-95),(-47,-100)).segment((-11,-62)).segment((-11,-61)).segment((-10,-61)).segment((-10,-60)).segment((-3,-51)).arc((12,-50),(13,-36)).segment((32,-19)).segment((31,-18)).segment((33,-18)).segment((53,36)).segment((48,38)).segment((56,60)).segment((52,61)).segment((44,39)).segment((40,36)).arc((39,37),(38,37)).segment((18,0)).segment((5,-7)).segment((6,-8)).segment((4,-8)).segment((4,-9)).segment((-3,-18)).segment((2,-21)).segment((-2,-24)).segment((-10,-24)).segment((-10,-25)).segment((-17,-34)).arc((-20,-39),(-21,-44)).close().assemble().finalize().extrude(-8).union(w0.sketch().arc((50,56),(55,77),(54,98)).close().assemble().finalize().extrude(-7))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0049_00495377.step')
