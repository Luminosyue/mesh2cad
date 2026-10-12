from visualize_native_v2 import *
rows=[read(p) for p in (O/'cases').glob('*/*/result.json')];near=[r for r in rows if r['v1_status']=='NEAR_PASS'];selected=[r for r in near if r['new_strict_vs_baseline']][:2]+sorted([r for r in near if r['status']=='NEAR_PASS'],key=lambda r:-r['metrics']['iou'])[:1]
out=[]
for r in selected:out.append(run(('near_to_strict' if r['status']=='STRICT_ACCEPT' else 'near_still_failed',r)))
dump(O/'visualizations/near_preview.json',out);print(out)
