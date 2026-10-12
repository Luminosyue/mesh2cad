#!/usr/bin/env python3
"""Read-only aggregate and fixed-30 audit of existing Dora fitted-curve outputs."""
from __future__ import annotations
import json,pathlib,hashlib
from collections import Counter,defaultdict
import numpy as np
ROOT=pathlib.Path('/data/home/cuiyuehan/project/mesh2cad');OUT=ROOT/'ours3/dora_input_data_audit_v1';BUILD=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1/cad'; V3=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_1k_train.json'
def q(x,p): return float(np.percentile(x,p)) if x else None
def category(r):
 ops=set(r.get('operation_names',[]));n=r.get('operation_count',0);src=r.get('source_dataset','')
 if src=='fusion360' and (n>=8 or r.get('m2_available_count',0)>=32):return 'complex'
 if n<=3:return 'simple'
 if 'Circle' in ops or r.get('has_circle') or r.get('has_hole'):return 'circle_hole'
 if ('Polygon' in ops or r.get('has_polygon')) and ('Cut' in ops or r.get('has_cut')):return 'polygon_cut'
 if 'Union' in ops or r.get('has_join') or n>=10:return 'multi_op'
 return 'medium'
def take(pool,cat,n,used):
 xs=sorted([r for r in pool if category(r)==cat and r['cad_id'] not in used],key=lambda r:hashlib.sha256((r['cad_id']+'|42').encode()).hexdigest());return xs[:n]
def main():
 inv=json.load(open(OUT/'DATA_INVENTORY.json')); rows=[r for r in inv['rows'] if r['provenance_status']=='PASS'];v3={r['cad_id']:r for r in json.load(open(V3))['records']};rows=[dict(r,**v3[r['cad_id']]) for r in rows]
 used=set();sel=[]
 for c in ('simple','circle_hole','polygon_cut','multi_op','medium'):
  x=take(rows,c,5,used);sel+=x;used|={r['cad_id'] for r in x}
 # force five high-complexity Fusion360; report a shortfall honestly.
 x=sorted([r for r in rows if r['source_dataset']=='fusion360' and r['cad_id'] not in used],key=lambda r:(-r.get('operation_count',0),-r.get('m2_available_count',0),hashlib.sha256((r['cad_id']+'|42').encode()).hexdigest()))[:5];sel+=x;used|={r['cad_id'] for r in x}
 # If a requested semantic bucket is genuinely short, fill deterministically
 # from all remaining provenance-pass records and retain the actual bucket label.
 if len(sel)<30:
  fill=sorted([r for r in rows if r['cad_id'] not in used],key=lambda r:hashlib.sha256((r['cad_id']+'|42').encode()).hexdigest())[:30-len(sel)]
  sel+=fill;used|={r['cad_id'] for r in fill}
 (OUT/'AUDIT30_MANIFEST.json').write_text(json.dumps({'seed':42,'selection':'fixed category ordering then SHA256(cad_id|42); complex bucket is highest operation/curve Fusion360','requested_per_bucket':5,'actual_counts':dict(Counter(category(r) for r in sel)),'count':len(sel),'records':[{'cad_id':r['cad_id'],'source_dataset':r['source_dataset'],'bucket':category(r),'operation_count':r.get('operation_count'),'operation_names':r.get('operation_names')} for r in sel]},indent=2)+'\n')
 types=Counter();classes=Counter();chains=[];edge=[];lens=[];res=[];valid=0;invalid=Counter();perc=[]
 for r in rows:
  b=BUILD/r['cad_id']; fm=json.load(open(b/'dora/fitted_curves.json')); cm=json.load(open(b/'dora/chains_meta.json')); co=json.load(open(b/'correspondence.json')); cr=json.load(open(b/'curve_c2/meta.json'))
  types.update(x.get('type','OTHER') for x in fm['curves']); classes.update(x.get('classification','UNMATCHED') for x in co['records']);chains.append(len(cm['chains']));edge.append(json.load(open(b/'dora/edge_graph_meta.json'))['n_edges']);lens += [float(x.get('length',0)) for x in fm['curves']];res += [float(x.get('normalized_residual',0)) for x in fm['curves']]
  arr=np.load(b/'curve_c2/curve_inputs.npy'); ok=arr.ndim==3 and arr.shape[1:]==(32,7) and np.isfinite(arr).all(); valid+=int(ok)*arr.shape[0]
  if not ok:invalid['schema_or_nonfinite']+=arr.shape[0]
  perc.append({'cad_id':r['cad_id'],'source':r['source_dataset'],'raw_edge_count':edge[-1],'raw_component_count':chains[-1],'fitted_curve_count':len(fm['curves']),'fitted_types':dict(Counter(x.get('type','OTHER') for x in fm['curves'])),'correspondence':dict(Counter(x.get('classification','UNMATCHED') for x in co['records'])),'c2_shape':list(arr.shape),'c2_valid':bool(ok),'c2_meta':cr})
 total=sum(types.values());matched=classes['MATCHED_1_TO_1']; gt=sum(len(json.load(open(BUILD/r['cad_id']/'gt_brep_curves.json'))['curves']) for r in rows)
 fit={'TOTAL_CHAINS':sum(chains),'TOTAL_DORA_FITTED_CURVES':total,'FILTERED_CHAINS':None,'FITTED_TYPES':dict(types),'FIT_FAILURES':None,'chain_per_cad':{'median':q(chains,50),'p90':q(chains,90)},'edge_per_cad':{'median':q(edge,50),'p90':q(edge,90)},'curve_length':{'median':q(lens,50),'p10':q(lens,10),'p90':q(lens,90)},'normalized_residual':{'median':q(res,50),'p90':q(res,90)},'component_to_fitted':'one fitted record per passing retained chain; see fitted curve chain_id','correspondence_classification':dict(classes)}
 gtvs={'GT_curve_count':gt,'Dora_curve_count':total,'GT_curve_coverage_proxy':matched/max(gt,1),'Dora_matched_ratio':matched/max(total,1),'matched_1_to_1':matched,'unmatched_Dora_count':classes['UNMATCHED'],'fragmentation_records':classes['FRAGMENTED'],'partial_records':classes['PARTIAL'],'merged_records':classes['MERGED'],'thresholds':'frozen existing correspondence.json; no thresholds changed'}
 c2={'TOTAL_DORA_FITTED_CURVES':total,'C2_INPUT_VALID':valid,'C2_INPUT_INVALID':sum(invalid.values()),'invalid_reasons':dict(invalid),'valid_rate':valid/max(total,1),'schema':'[N,32,7] local_xyz+tangent+s','global_placement_preserved':'NO','evidence':'curve_c2/meta.json explicitly normalizes local xyz by curve-local center and max extent; global centroid/bbox exist separately only as anchors.npy [N,6].'}
 (OUT/'DORA_FITTING_AUDIT.json').write_text(json.dumps(fit,indent=2)+'\n');(OUT/'per_cad_fitting.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in perc));(OUT/'GT_VS_DORA_BASELINE.json').write_text(json.dumps(gtvs,indent=2)+'\n');(OUT/'C2_INTERFACE_AUDIT.json').write_text(json.dumps(c2,indent=2)+'\n');
 ex=[]
 for r in perc[:10]:
  a=np.load(BUILD/r['cad_id']/'curve_c2/curve_inputs.npy'); ex.append(r['cad_id']+' '+str(a.shape)+'\n'+np.array2string(a[0,:5],precision=5)+'\n')
 (OUT/'C2_INTERFACE_EXAMPLES.txt').write_text('\n'.join(ex));print(json.dumps({'audit30':len(sel),'fitted':total,'types':dict(types),'matched':matched,'c2_valid':valid},indent=2))
if __name__=='__main__':main()
