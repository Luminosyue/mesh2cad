import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,31))
r=w0.sketch().arc((-100,-6),(-74,-67),(-16,-99)).segment((-16,-100)).segment((16,-100)).segment((16,-99)).arc((74,-67),(100,-6)).segment((100,6)).segment((100,10)).segment((99,10)).arc((80,60),(38,93)).segment((38,94)).segment((36,94)).arc((0,100),(-36,94)).segment((-38,94)).segment((-38,93)).arc((-74,67),(-99,23)).segment((-68,42)).segment((-58,25)).arc((-66,-13),(-38,-42)).segment((-38,-43)).segment((-36,-43)).arc((0,-55),(36,-43)).segment((38,-43)).segment((38,-42)).arc((53,-24),(63,-3)).segment((16,-28)).segment((6,-11)).arc((14,16),(-10,30)).segment((-16,39)).segment((-16,38)).arc((-26,44),(-38,48)).segment((-38,49)).segment((-40,49)).segment((-47,88)).arc((-58,81),(-68,72)).segment((-79,62)).segment((-68,50)).arc((-75,35),(-79,19)).segment((-99,-10)).close().assemble().finalize().extrude(-62)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0094_00949180.step')
