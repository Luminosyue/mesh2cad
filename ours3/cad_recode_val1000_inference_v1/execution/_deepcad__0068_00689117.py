import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(20,0,0))
w1=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().arc((-33,35),(-4,25),(-12,53)).arc((-23,41),(-33,35)).assemble().finalize().extrude(75).union(w0.sketch().arc((-47,-8),(-44,-18),(-38,-27)).segment((-38,-35)).segment((-32,-35)).arc((-10,-13),(20,-20)).segment((20,-19)).arc((47,7),(29,38)).arc((24,40),(20,42)).segment((20,46)).segment((10,46)).arc((-1,32),(-18,33)).arc((-20,32),(-22,31)).arc((-4,18),(-13,-2)).segment((-13,-8)).close().assemble().finalize().extrude(80)).union(w1.sketch().arc((-96,27),(-99,-11),(-86,-46)).segment((-86,-47)).segment((-85,-47)).arc((-60,-69),(-29,-80)).arc((-26,-23),(22,1)).arc((-23,52),(-86,43)).segment((-86,44)).arc((-90,37),(-94,30)).arc((-96,29),(-96,27)).assemble().finalize().extrude(-48))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00689117.step')
