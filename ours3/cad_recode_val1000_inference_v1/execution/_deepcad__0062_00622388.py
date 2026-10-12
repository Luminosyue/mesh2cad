import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(96,0,0))
w1=cq.Workplane('ZX',origin=(0,0,0))
r=w0.sketch().segment((-22,37),(-20,27)).arc((-21,10),(-14,-5)).segment((-12,-15)).segment((-1,-13)).arc((1,-13),(3,-12)).segment((14,-10)).segment((12,-1)).arc((13,16),(5,31)).segment((3,42)).segment((-8,40)).arc((-10,40),(-12,39)).close().assemble().finalize().extrude(-16).union(w0.sketch().segment((-22,25),(-16,-12)).segment((22,-8)).segment((16,42)).segment((-21,42)).arc((-19,33),(-22,25)).assemble().finalize().extrude(4)).union(w1.sketch().segment((-47,-43),(-36,-43)).arc((-35,-56),(-29,-68)).segment((-29,-84)).segment((-47,-84)).segment((-47,-100)).segment((-21,-100)).segment((-21,-93)).arc((13,-89),(4,-55)).arc((1,-41),(-10,-31)).segment((-10,-29)).arc((15,-23),(-10,-17)).segment((-10,-12)).segment((10,-12)).segment((10,35)).segment((-22,35)).segment((-22,20)).segment((-47,20)).segment((-47,-1)).segment((-47,-29)).close().assemble().finalize().extrude(-5))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0062_00622388.step')
