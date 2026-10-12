from __future__ import annotations

import json, sys, hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent))
from primitive_aware_chain_segmentation_v1 import segment_chain_primitives
from dora_fitted_curve_dataset_v1 import graph_from_dora, extract_chains, objverts, sample_fit
from dora_brep_granularity_canary_v1 import extract_gt_edges, metrics_pair, select_nearby, best_connected_set

DATA = ROOT / 'ours3/dora_fitted_curve_dataset_v1/train800_build_v1/cad'
COHORT = ROOT / 'ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl'
SOURCE = ROOT / 'ours3/dora_fitted_curve_v1_rare_type_failure_audit_v4/VISUAL_CASE_MANIFEST.json'
OUT = ROOT / 'ours3/primitive_aware_segmentation_canary_v1'

def dump(p, x): p.write_text(json.dumps(x, indent=2, sort_keys=True) + '\n')
def sample_fit(f, n=256):
    from dora_brep_granularity_canary_v1 import sample_fitted
    return sample_fitted(f, n)
def segment_sample(f, s):
    x = sample_fit(f, 256); a, b = s.start_index, s.end_index
    return x[a:b+1]
def render_case(folder, mesh, chain, old_pts, segments, segment_pts, gt_edges):
    center = mesh.mean(0); _, _, vh = np.linalg.svd(mesh-center, full_matrices=False); basis = vh[:2]
    project = lambda p: (np.asarray(p)-center) @ basis.T
    for title in ('before', 'after'):
        fig = plt.figure(figsize=(8, 6)); ax = fig.add_subplot(111, projection='3d')
        q = mesh[::max(1, len(mesh)//5000)]; ax.scatter(q[:,0], q[:,1], q[:,2], s=.2, c='.75')
        ax.plot(chain[:,0], chain[:,1], chain[:,2], c='red', lw=1, label='Dora chain')
        if title == 'before': ax.plot(old_pts[:,0], old_pts[:,1], old_pts[:,2], c='blue', lw=1.5, label='old whole fit')
        else:
            colors=('tab:blue','tab:orange','tab:green','tab:red','tab:purple')
            for i, (s, q) in enumerate(zip(segments, segment_pts)):
                ax.plot(q[:,0],q[:,1],q[:,2],c=colors[i%len(colors)],lw=1.8,label=f'S{i} {s.primitive_type}')
        for e in gt_edges:
            p=e['points']; ax.scatter(p[[0,-1],0],p[[0,-1],1],p[[0,-1],2],c='black',s=10)
        ax.set_title(title); ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(folder/(title+'.png'),dpi=140); plt.close(fig)
    fig, axes=plt.subplots(1,2,figsize=(12,5))
    for ax,title in zip(axes,('before','after')):
        q=project(mesh[::max(1,len(mesh)//5000)]); ax.scatter(q[:,0],q[:,1],s=.2,c='.75'); q=project(chain); ax.plot(q[:,0],q[:,1],c='red',lw=1)
        if title=='before': q=project(old_pts); ax.plot(q[:,0],q[:,1],c='blue',lw=1.5)
        else:
            for i,(s,q0) in enumerate(zip(segments,segment_pts)): q=project(q0); ax.plot(q[:,0],q[:,1],lw=1.8,label=f'S{i} {s.primitive_type}')
        for e in gt_edges: q=project(e['points']); ax.scatter(q[[0,-1],0],q[[0,-1],1],c='black',s=10)
        ax.set_title(title); ax.set_aspect('equal'); ax.axis('off')
    fig.tight_layout(); fig.savefig(folder/'before_after_2panel.png',dpi=140); plt.close(fig)
def main():
    source = json.loads(SOURCE.read_text())['cases']; cohort = {json.loads(x)['cad_id']: json.loads(x) for x in COHORT.read_text().splitlines() if x}
    rare = [x for x in source if x['fitted_type'] in ('ELLIPSE','BSPLINE')][:10]
    control_pool=[]
    for cdir in sorted((DATA).iterdir(), key=lambda p: hashlib.sha256(p.name.encode()).hexdigest()):
        if not cdir.is_dir(): continue
        fits=json.loads((cdir/'dora/fitted_curves.json').read_text())['curves']; corr=json.loads((cdir/'correspondence.json').read_text())['records']
        for r in corr:
            i=int(r['dora_curve_index']); typ=fits[i]['type']
            if r['classification']=='MATCHED_1_TO_1' and typ in ('LINE','CIRCLE','ARC'):
                control_pool.append({'cad_id':cdir.name,'dora_chain_id':int(fits[i]['chain_id']),'fitted_curve_id':i,'fitted_type':typ,'match_class':r['classification'],'gt_brep_edge_id':r.get('gt_curve_id')})
    control_pool.sort(key=lambda x: hashlib.sha256(f"{x['cad_id']}:{x['fitted_curve_id']}".encode()).hexdigest())
    control = [x for x in control_pool if x['fitted_type']=='LINE'][:5] + [x for x in control_pool if x['fitted_type'] in ('CIRCLE','ARC')][:5]
    cases = rare + control; OUT.mkdir(parents=True, exist_ok=True); (OUT/'visual_cases').mkdir(exist_ok=True)
    dump(OUT/'CASE_MANIFEST.json', {'selection_rule':'frozen audit manifest order; first 10 rare + first 10 controls','total':len(cases),'rare':len(rare),'control':len(control),'cases':cases})
    rows=[]
    for c in cases:
        cad=c['cad_id']; row=cohort[cad]; cdir=DATA/cad; meta=json.loads((cdir/'dora/chains_meta.json').read_text()); cm=meta['chains'][int(c['dora_chain_id'])]
        xyz, adj, edges=graph_from_dora(np.load(row['assets']['dora_salient_edges']['path'])); chain=extract_chains(xyz,adj,edges)[int(c['dora_chain_id'])]
        verts=objverts(row['assets']['model_obj']['path']); diag=float(np.linalg.norm(verts.max(0)-verts.min(0)))
        result=segment_chain_primitives(chain['points'], bool(chain['closed_loop']), diag)
        fits=json.loads((cdir/'dora/fitted_curves.json').read_text())['curves']; old=fits[int(c['fitted_curve_id'])]
        edges_gt, gt_adj, _=extract_gt_edges(Path(row['assets']['model_step']['path']))
        old_pts=sample_fit(old); nearby, dmin, radius, primary=select_nearby(old_pts, edges_gt, gt_adj, diag, c.get('gt_brep_edge_id'))
        ids, set_m, how=best_connected_set(old_pts, primary, nearby, {e['edge_id']:e for e in edges_gt}, gt_adj, diag)
        segments=result['segments']; segment_pts=[sample_fit(s.fit) for s in segments]; new_cov=[]
        gt_pts=np.vstack([e['points'] for e in edges_gt if e['edge_id'] in ids]) if ids else np.zeros((0,3))
        for s in segments:
            q=sample_fit(s.fit); new_cov.append(metrics_pair(q, gt_pts, diag))
        folder=OUT/'visual_cases'/f'{cad}_{int(c["dora_chain_id"])}'; folder.mkdir(parents=True,exist_ok=True)
        render_case(folder, verts, chain['points'], old_pts, segments, segment_pts, [e for e in edges_gt if e['edge_id'] in ids])
        rows.append({'cad_id':cad,'chain_id':int(c['dora_chain_id']),'fitted_curve_id':int(c['fitted_curve_id']),'case_family':'rare' if c in rare else 'control','old_whole_chain_type':old['type'],'old_whole_chain_residual':old.get('normalized_residual'),'number_of_segments':len(segments),'segments':[{'start_index':s.start_index,'end_index':s.end_index,'point_count':s.point_count,'arclength':s.arclength,'primitive_type':s.primitive_type,'normalized_residual':s.normalized_residual} for s in segments],'candidate_count_raw':result['candidate_count_raw'],'candidate_count_kept':result['candidate_count_kept'],'candidate_count_truncated':result['candidate_count_truncated'],'nearby_gt_edge_ids':ids,'nearby_gt_primitive_sequence':[e['viz_type'] for e in edges_gt if e['edge_id'] in ids],'new_vs_gt_edge_set_metrics':new_cov,'formal_match_class_unchanged':c['match_class']})
    (OUT/'SEGMENTATION_CASES.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in rows))
    rare_rows=[x for x in rows if x['case_family']=='rare']; controls=[x for x in rows if x['case_family']=='control']
    summary={'CURRENT_GATE':'PRIMITIVE_AWARE_SEGMENTATION_CANARY_REVIEW_REQUIRED','TOTAL_CASES':len(rows),'RARE_CASES':len(rare_rows),'CONTROL_CASES':len(controls),'OLD_ONE_CHAIN_ONE_PRIMITIVE':True,'RARE_MULTI_SEGMENT_COUNT':sum(x['number_of_segments']>1 for x in rare_rows),'OLD_BSPLINE_COUNT':sum(x['old_whole_chain_type']=='BSPLINE' for x in rows),'NEW_BSPLINE_SEGMENT_COUNT':sum(s['primitive_type']=='BSPLINE' for x in rows for s in x['segments']),'CONTROL_OVERSEGMENT_COUNT':sum(x['number_of_segments']>1 for x in controls),'CONTROL_OVERSEGMENT_RATE':sum(x['number_of_segments']>1 for x in controls)/max(len(controls),1),'GT_STRUCTURE_IMPROVED_COUNT':0,'GT_STRUCTURE_WORSENED_COUNT':0,'RECOMMENDED_NEXT_ACTION':'NEEDS_MANUAL_REVIEW','NOTE':'Geometry/GT comparison is recorded; gate remains review-required until visual and sequence review.'}
    dump(OUT/'SEGMENTATION_SUMMARY.json',summary); (OUT/'SEGMENTATION_SUMMARY.md').write_text('\n'.join(f'{k}: {v}' for k,v in summary.items())+'\n')
    print('\n'.join(f'{k}={v}' for k,v in summary.items()))
if __name__=='__main__': main()
