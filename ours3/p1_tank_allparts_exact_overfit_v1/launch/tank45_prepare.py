from pathlib import Path
import sys,json,ast,subprocess,csv,statistics
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_tank_allparts_exact_overfit_v1');sys.path.insert(0,str(E/'launch'));import a2_runtime as rt
rt.prepare();inv=json.loads((E/'data/block_inventory.json').read_text());print('blocks',len(inv),'tokens',sum(x['token_count'] for x in inv));
parts=sorted({x['part'] for x in inv});print('parts',len(parts),parts[:3],parts[-3:]);
rows=[]
for p in parts:
 rs=[x for x in inv if x['part']==p];rows.append({'PART_ID':p,'GT_BLOCK_COUNT':len(rs),'GT_TOKEN_COUNT':sum(x['token_count'] for x in rs)})
with (E/'tank_allparts_dataset_audit.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(E/'tank_allparts_dataset_audit.json').write_text(json.dumps({'parts':rows,'TOTAL_PART_N':len(parts),'TOTAL_BLOCK_N':len(inv),'TOTAL_TOKEN_N':sum(x['token_count'] for x in inv),'MIN_BLOCK_N':min(x['GT_BLOCK_COUNT'] for x in rows),'MAX_BLOCK_N':max(x['GT_BLOCK_COUNT'] for x in rows),'MEDIAN_BLOCK_N':statistics.median(x['GT_BLOCK_COUNT'] for x in rows),'MIN_TOKEN_N':min(x['GT_TOKEN_COUNT'] for x in rows),'MAX_TOKEN_N':max(x['GT_TOKEN_COUNT'] for x in rows),'MEDIAN_TOKEN_N':statistics.median(x['GT_TOKEN_COUNT'] for x in rows)},indent=2))
