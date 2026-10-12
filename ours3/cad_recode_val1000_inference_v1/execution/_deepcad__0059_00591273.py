import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,8))
r=w0.sketch().segment((-89,-100),(-50,-100)).segment((-50,-67)).segment((-65,-67)).segment((-65,-54)).segment((-73,-54)).segment((-73,-23)).segment((-65,-23)).segment((-65,-10)).segment((-50,-10)).segment((-50,13)).segment((-25,13)).segment((-25,-10)).segment((-18,-10)).segment((-18,-23)).segment((-9,-23)).segment((-9,-54)).segment((-18,-54)).segment((-18,-67)).segment((13,-67)).segment((13,-100)).segment((16,-100)).segment((16,-58)).segment((13,-58)).segment((13,-38)).segment((45,-38)).segment((45,-67)).segment((53,-67)).segment((53,-100)).segment((88,-100)).segment((88,100)).segment((-34,100)).segment((8,53)).segment((-10,53)).segment((-10,48)).segment((-30,48)).segment((-30,53)).segment((-50,53)).segment((-50,100)).segment((-89,100)).segment((-89,65)).segment((-73,53)).segment((-89,31)).close().assemble().push([(10,24)]).circle(33,mode='s').push([(78,24)]).rect(20,28,mode='s').finalize().extrude(-16)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0059_00591273.step')
