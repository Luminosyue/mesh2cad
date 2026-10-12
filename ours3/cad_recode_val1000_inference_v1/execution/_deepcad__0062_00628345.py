import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,1,0))
r=w0.sketch().segment((-16,100),(-15,51)).arc((-16,45),(-15,39)).segment((-13,-28)).arc((-14,-40),(-13,-52)).segment((-15,-52)).segment((-14,-63)).segment((-12,-63)).arc((-11,-65),(-10,-67)).segment((-15,-67)).segment((-14,-78)).segment((-11,-78)).segment((-11,-89)).segment((-14,-89)).segment((-14,-100)).segment((14,-96)).segment((13,-85)).arc((16,-40),(-12,-10)).segment((-12,-6)).segment((16,13)).segment((15,39)).arc((16,45),(15,51)).segment((13,100)).close().assemble().finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0062_00628345.step')
