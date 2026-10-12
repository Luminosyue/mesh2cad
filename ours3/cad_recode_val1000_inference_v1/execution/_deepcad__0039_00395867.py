import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,52))
r=w0.sketch().arc((-16,-4),(-15,-7),(-12,-11)).close().assemble().reset().face(w0.sketch().segment((-12,12),(-7,12)).segment((-8,15)).arc((-10,13),(-12,12)).assemble()).reset().face(w0.sketch().segment((-12,11),(-6,1)).arc((-6,-5),(-2,-8)).segment((2,-17)).segment((13,-11)).segment((11,-8)).arc((15,-7),(16,-4)).segment((12,-4)).segment((12,-3)).segment((16,-3)).arc((15,6),(8,14)).segment((8,15)).segment((7,15)).segment((7,16)).segment((6,15)).segment((5,15)).segment((5,14)).close().assemble()).finalize().extrude(-170).union(w1.sketch().arc((-16,3),(15,-7),(-14,8)).arc((-13,5),(-16,3)).assemble().circle(8,mode='s').finalize().extrude(-152))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0039_00395867.step')
