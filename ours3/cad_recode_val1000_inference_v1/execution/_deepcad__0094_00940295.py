import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-98,-35),(-68,-42)).segment((-64,-27)).arc((-42,-14),(-41,12)).segment((-32,-39)).segment((-16,-36)).segment((-16,-42)).segment((-7,-42)).segment((-7,-34)).segment((23,-31)).segment((23,-42)).segment((24,-42)).segment((24,-31)).segment((62,-42)).segment((67,-22)).segment((100,-22)).segment((100,36)).segment((92,36)).segment((92,37)).segment((62,42)).segment((58,36)).segment((24,36)).segment((24,38)).segment((23,38)).segment((23,36)).segment((-7,36)).segment((-7,38)).segment((-16,38)).segment((-16,32)).segment((-33,42)).segment((-40,27)).arc((-52,34),(-66,36)).segment((-66,38)).segment((-76,38)).segment((-76,36)).arc((-100,26),(-82,8)).arc((-91,-10),(-96,-30)).close().assemble().push([(61,10)]).circle(16,mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0094_00940295.step')
