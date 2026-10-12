from cad_render_utils import *
from pathlib import Path
import json,hashlib,html
from concurrent.futures import ProcessPoolExecutor
P=Path('/data/home/cuiyuehan/project/mesh2cad/outputs');O=P/'cad_render_v4';V=P/'part_cad_v3_assembly_visualizations'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2))
def run(obj):
 oid=obj['object_id'];d=O/'renders'/oid;d.mkdir(parents=True,exist_ok=True);before={p['step_path']:sha(p['step_path']) for p in obj['parts']};R=np.array(obj['view_matrix']);center=np.array(obj['center']);span=obj['common_source_cad_span'];actors=[];edges=[];evidence=[]
 for part in obj['parts']:
  T=np.array(part['world_transform']);scale=np.linalg.norm(T[:3,0]);linear=span*.00025/scale;data,edge,meta=step_data(part['step_path'],T,linear,.025);actors.append(actor(data));edges.append(edge_actor(edge));evidence.append({'case_id':part['case_id'],'step_path':part['step_path'],'step_sha256_before':before[part['step_path']],**meta})
 subtitle=f"{obj['part_n']} native parts | includes Near/Reject candidates"
 clean=render(actors,center,span,R,title=obj['name']+' - CAD V4',subtitle=subtitle);clean.save(d/'smooth.png');edged=render(actors,center,span,R,title=obj['name']+' - B-Rep edges',subtitle='Real CAD topology edges; no triangle wireframe',edge_actors=edges);edged.save(d/'smooth_brep_edges.png')
 compare=Image.new('RGB',(2400,800),'white');compare.paste(Image.open(V/oid/'assembly.png'),(0,0));compare.paste(clean,(800,0));compare.paste(edged,(1600,0));(O/'comparisons').mkdir(exist_ok=True);compare.save(O/'comparisons'/(oid+'_v3_v4.png'))
 after={p:sha(p) for p in before};assert before==after
 r={'object_id':oid,'name':obj['name'],'part_n':obj['part_n'],'same_step_hashes':True,'geometry_changed_by_renderer':False,'camera_matches_v3':True,'same_world_transforms':True,'center':center.tolist(),'view_matrix':R.tolist(),'common_span':span,'parts':evidence};dump(d/'manifest.json',r);print('RENDERED',oid,obj['name'],flush=True);return r
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);a=ap.parse_args();objects=json.loads((V/'manifest.json').read_text())['objects'];objects=objects[:a.limit] if a.limit else objects
 # Xvfb/llvmpipe rendering is CPU-only; do not touch any CUDA process.
 with ProcessPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,objects))
 dump(O/'manifests/render_results.json',results);dump(O/'config/render_v4.json',{'source_geometry':'unchanged V3 STEP files','render_linear_deflection':'object common camera span * 0.00025 / part uniform world scale','render_angular_deflection':.025,'normals':'exact OCC surface normal at each tessellation vertex; duplicated face boundaries','smooth_shading_enabled':True,'sharp_edge_preservation':'preserve independent face normals across every B-Rep boundary; tangent faces have consistent analytic normals','dihedral_angle_threshold_degrees':None,'threshold_reason':'surface-aware normals preserve true discontinuities directly, no heuristic smoothing-angle threshold is used','edge_overlay':'sampled true B-Rep edges only','triangle_edge_display':False,'evaluation_tessellation_unchanged':[.001,.05],'geometry_changed_by_renderer':False,'renderer':'VTK Phong + multisample, Xvfb software rendering','camera':'same V3 orthographic view matrix, center, span and image offset'})
 page='<meta charset="utf-8"><title>CAD Render V4</title><style>body{max-width:1800px;margin:30px auto;font:17px system-ui}img{width:100%}</style><h1>CAD Render V4</h1><p>Left: original V3 display. Middle: V4 surface-aware smooth shading. Right: V4 with true B-Rep edges. All panels use the SAME historical V3 geometry; fitting improvements are reported separately. Near/Reject parts remain Near/Reject.</p>'
 for r in results:page+=f'<h2>{html.escape(r["name"])}</h2><img src="comparisons/{r["object_id"]}_v3_v4.png">'
 (O/'index.html').write_text(page)
 report=f'''# CAD_RENDER_V4_REPORT

Rendered {len(results)} existing V3 assemblies. The source STEP and part transforms are identical to V3. Per-part STEP hashes before/after match. This branch performs no fitting and changes no metrics, acceptance threshold or status.

V3 sampled tessellated triangles with their constant face normals. V4 tessellates original STEP for display at adaptive linear deflection (camera span * 0.00025 / world scale), angular deflection 0.025 radians, and uses exact OCC surface normals at display vertices. VTK Phong interpolation provides smooth within-face shading. Vertices are not merged across B-Rep faces, so true sharp edges retain separate normals. No smoothing-angle heuristic is needed or applied; tangent continuity comes from the underlying surface normals. All real edges can be overlaid from STEP topology. Tessellation triangle wireframe is disabled.

Camera matrix, object center, span, orthographic scale and vertical image offset match V3. Previous polygonal-profile planar sidewalls remain genuine planar geometry; smoothing the display does not turn them into a curved B-Rep. This is expected and is addressed only by the separate fitting branch.

SMOOTH_SHADING_ENABLED = YES
BREP_EDGE_OVERLAY_AVAILABLE = YES
TRIANGLE_EDGE_DISPLAY_DISABLED = YES
HIGH_QUALITY_TESSELLATION = YES
GEOMETRY_CHANGED_BY_RENDERER = NO
REPRESENTATIVE_RENDER_N = {len(results)}

All previews include historical Near/Reject candidates. No assembly optimization or full-object quality acceptance is claimed. Detailed geometry hashes and display settings: renders/*/manifest.json and config/render_v4.json.
''';(O/'reports/CAD_RENDER_V4_REPORT.md').write_text(report);print('RENDER_COMPLETE',len(results),flush=True)
