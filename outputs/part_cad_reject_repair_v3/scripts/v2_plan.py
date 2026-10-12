from v2_common import *
import argparse
F={'A':'A_SIMPLE_PRIMITIVE','B':'B_EXTRUSION','C':'C_REVOLVE','D':'D_EXTRUDE_WITH_CUTS','E':'E_BOOLEAN_COMPOSITION','F':'F_MULTI_PRIMITIVE','G':'G_FRAME_BEAM','H':'H_FREEFORM_OR_UNSUPPORTED'}
ap=argparse.ArgumentParser();ap.add_argument('--group',choices=['near','reject','strict'],required=True);a=ap.parse_args();mapping={'near':'NEAR_PASS','reject':'REJECT','strict':'STRICT_ACCEPT'}
policy={'author':'interactive Codex assistant','scope':a.group,'policy':'Near-pass: retain observed native construction and optimize parameters; hypotheses of missing topology are not proof and do not authorize switching family. Reject: use measured normal/section/component evidence to select bounded alternatives; no case-ID-specific numeric fitting. Strict: retain V1 geometry.','model_call_scope':'batch-level structure policy authored after inspection of diagnostic summaries; per-case label reconciliation below is deterministic; no separate per-part API calls claimed','numeric_parameters':'determined only by geometry code','uncalibrated_confidence':True}
dump(O/'manifests'/f'planning_policy_{a.group}.json',policy)
for row in read(O/'manifests/cases.json'):
 if row['v1_status']!=mapping[a.group]:continue
 d=O/'cases'/row['case_id'];p=d/'diagnosis/structure_plan.json'
 if p.exists():continue
 r=read(d/'source/v1_result.json');kind=r['best_kind'];letter='C' if kind=='revolve' else 'D' if kind=='extrusion_with_cuts' else 'B' if kind in ['extrusion','section_loft'] else 'F' if kind=='multi_primitive' else 'A';reason='Reconcile previous hypothesized family with the actual selected native program; optimize its parameters first.'
 f=read(d/'features/features_v2.json') if (d/'features/features_v2.json').exists() else {}
 if letter in ['A','B'] and r['cad_family'].startswith(('F_','G_')):letter='G'
 if a.group=='reject':
  fits=[x for x in f['cylinder_fits'] if 'radius' in x];best=min(fits,key=lambda x:x['relative_radial_mad'],default=None);planarity=sum(x['area_fraction'] for x in f['normal_clusters'][:6]);holes=max(s['stable_hole_count'] for s in f['cross_sections']);closed=max(sum(x['closed_loops']>0 for x in s['sections']) for s in f['cross_sections'])
  if f['component_n']>1 and f['component_n']<=7:letter='F'
  elif holes:letter='D'
  elif best and best['relative_radial_mad']<.06 and best['side_sample_fraction']>.35:letter='G' if max(f['aspect_ratios'][1:])<.25 else 'C'
  elif planarity>.65:letter='B'
  elif closed>=3:letter='B'
  else:letter='H'
  reason='Reclassify rejected geometry from side-normal/radial evidence, stable nested sections, planarity and observed connected components; unsupported is a legitimate outcome.'
 plan={'case_id':row['case_id'],'cad_family_v1':r['cad_family'],'cad_family_v2':F[letter],'family_changed':r['cad_family'].split('_',1)[0]!=letter,'family_confidence':.65 if a.group!='reject' else .5,'family_reason':reason,'structure_switch_allowed':a.group=='reject','construction_plan':['Preserve original part coordinate frame and source bytes','Fit plane/origin/axis and primitive or bounded sketch dimensions from geometry','Use bounded local parameter search','Rebuild native CadQuery, export STEP and reload before final comparison','Keep V1 baseline if refinement does not improve the frozen score'], 'planning_provenance':policy}
 dump(p,plan)
print('PLANS_READY',a.group)
