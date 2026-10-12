import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('YZ',origin=(88,0,0))
r=w0.sketch().segment((-58,0),(-49,-3)).arc((-35,-36),(-3,-51)).segment((-3,-58)).arc((-35,46),(56,-15)).segment((46,-15)).arc((47,-17),(47,-19)).segment((56,-19)).arc((52,-25),(47,-31)).arc((46,-33),(46,-34)).segment((47,-34)).arc((46,-36),(44,-37)).arc((40,-38),(37,-43)).arc((40,-40),(42,-36)).segment((43,-36)).segment((57,-10)).segment((49,-7)).arc((48,1),(46,9)).segment((56,9)).arc((46,34),(26,51)).segment((26,44)).arc((-16,46),(-46,19)).segment((-55,21)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-58,3),(-49,3)).arc((0,50),(49,3)).segment((58,3)).arc((0,58),(-58,3)).assemble().finalize().extrude(-54)).union(w1.sketch().arc((-28,-50),(10,-57),(42,-36)).arc((34,-37),(26,-37)).arc((-10,-48),(-46,-27)).arc((-48,-29),(-49,-31)).arc((-44,-35),(-39,-38)).arc((-32,-47),(-28,-50)).assemble().finalize().extrude(-181))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0071_00711354.step')
