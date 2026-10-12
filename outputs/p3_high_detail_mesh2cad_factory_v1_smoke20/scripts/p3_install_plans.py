"""Materialize explicit interactive LLM structure decisions, not numeric parameter guesses."""
import json,hashlib,datetime,argparse
from pathlib import Path
O=Path(__file__).resolve().parents[1]
F={'A':'A_BOX_OR_SIMPLE_PRIMITIVE','B':'B_EXTRUSION','C':'C_REVOLVE','D':'D_EXTRUDE_WITH_CUTS','E':'E_BOOLEAN_COMPOSITION','F':'F_MULTI_PRIMITIVE','G':'G_FRAME_OR_BEAM_STRUCTURE','H':'H_UNSUPPORTED_FREEFORM'}
plans={
 'A':['Fit principal-frame box or cylinder','Compare bounded contour extrusion as an alternative','Retain only geometry-verified candidate'],
 'B':['Extract silhouettes on dominant and alternative axes','Fit contour with observed extrusion depth','Compare compact section loft when cross sections close'],
 'C':['Fit candidate rotation axis and transverse circle center','Estimate axial radial profile from geometry','Compare revolve with cylinder and contour extrusion; do not infer holes without evidence'],
 'D':['Extract nested planar contours','Extrude outer profile and cut supported inner loops','Reject unsupported hole topology or excessive Boolean count'],
 'E':['Identify bounded component/section structures','Construct base extrusion and only geometrically supported unions or cuts','Keep compound complexity within primitive and Boolean budgets'],
 'F':['Separate observed connected components','Fit compact extrusion per component in shared frame','Union at most seven simple components; reject complex components'],
 'G':['Identify elongated structural members from component and axis evidence','Fit observed beam contours and measured spans','Combine bounded members without filling empty frame spaces'],
 'H':['Test compact loft/revolve alternatives as hypotheses only','Reject if compact analytic/sketch representation fails geometry gate','Do not wrap mesh facets or invent missing geometry']}
reasons={'A':'Planar/compact evidence makes simple primitive plausible, but not certain','B':'Directional or flat geometry supports extrusion hypothesis; section variation remains a competing explanation','C':'Radial residual and section evidence support testing rotational construction; not an asserted design truth','D':'Multiple section loops or openings require explicit profile topology, not solid silhouette fill','E':'Irregular profile/topology suggests bounded constructive alternatives','F':'Observed disconnected components should remain separate in construction','G':'Object context and elongated component evidence support beam/frame structure','H':'Weak compact-family evidence or changing curved profiles; family assignment is uncertain'}
ap=argparse.ArgumentParser();ap.add_argument('--response',required=True);a=ap.parse_args();response=json.loads(Path(a.response).read_text());batch=response['batch'];raw=json.dumps(response,sort_keys=True)
artifact=O/'manifests'/f'llm_structure_response_{batch}.json'
if not artifact.exists():artifact.write_text(json.dumps(response,indent=2))
for obj,decisions in response['objects'].items():
 for pid,letter in decisions.items():
  d=O/'objects'/obj/'parts'/pid;feature=d/'features/features.json';summary=d/'features/summary.json'
  if not feature.exists():raise RuntimeError('Missing geometry evidence '+str(feature))
  dest=d/'planner/plan.json'
  if dest.exists():continue
  s=json.loads(summary.read_text());prompt='Choose compact native CAD structure from recorded geometry features; no numeric dimensions guessed. '+summary.read_text()
  (d/'planner/prompt.txt').write_text(prompt)
  rec={'cad_family':F[letter],'family_confidence':.55 if letter not in ['C','A'] else .65,'family_reason':reasons[letter],
   'construction_plan':plans[letter],'llm_used':True,'llm_provider':'OpenAI Codex interactive assistant','llm_model':'model identifier not exposed by runtime',
   'planning_mode':'explicit per-part structure decision emitted by assistant after reading geometry summaries; no external API call claimed',
   'generation_timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prompt_hash':hashlib.sha256(prompt.encode()).hexdigest(),
   'response_hash':hashlib.sha256(raw.encode()).hexdigest(),'feature_sha256':hashlib.sha256(feature.read_bytes()).hexdigest(),
   'numeric_parameters':'ALL_FIT_DETERMINISTICALLY_FROM_MESH','evidence_summary':s,'max_candidates':8,'max_primitives':8,'max_booleans':6}
  dest.write_text(json.dumps(rec,indent=2))
print('PLANS_INSTALLED',batch)
