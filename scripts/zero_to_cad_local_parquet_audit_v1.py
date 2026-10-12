from __future__ import annotations
import ast, hashlib, json, re
from pathlib import Path
P=Path('/data/home/cuiyuehan/project/mesh2cad/zerocad/89_93ae18509d914a69bf2646431db2c6ab_000014_000000-0.parquet')
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/zero_to_cad_local_parquet_audit_v1'); OUT.mkdir(parents=True,exist_ok=True)
def write(n,x): (OUT/n).write_text(json.dumps(x,indent=2,default=str)+'\n')
def digest(b): return hashlib.sha256(b).hexdigest()
def summary(v):
 if isinstance(v,(bytes,bytearray)): return {'type':'bytes','size':len(v),'sha256':digest(bytes(v))}
 if isinstance(v,(list,tuple)): return {'type':type(v).__name__,'length':len(v),'sample_types':[type(x).__name__ for x in v[:5]]}
 if isinstance(v,dict): return {'type':'dict','keys':sorted(map(str,v.keys()))[:30]}
 return {'type':type(v).__name__,'string_length':len(v) if isinstance(v,str) else None,'preview':v[:200] if isinstance(v,str) else None}
def classify(src):
 s=src.decode('utf-8','ignore') if isinstance(src,(bytes,bytearray)) else str(src)
 try: t=ast.parse(s)
 except Exception: return 'UNKNOWN',[],str(s)[:2000]
 calls=[ast.unparse(n.func) for n in ast.walk(t) if isinstance(n,ast.Call)]
 low=' '.join(calls).lower(); ops=[x for x in ['extrude','revolve','fillet','chamfer','union','cut','loft','sweep','shell','pattern'] if x in low]
 if 'export' in low and not any(x in low for x in ['workplane','box','rect','circle','polyline']): typ='EXPORT_WRAPPER'
 elif any(x in low for x in ['builder','build','load','import']): typ='BUILDER_WRAPPER'
 elif any(x in low for x in ['workplane','box','rect','circle','polyline','extrude','revolve','fillet','chamfer']): typ='DIRECT_CONSTRUCTION'
 else: typ='UNKNOWN'
 return typ,sorted(set(ops)),s[:2000]
def main():
 if not P.exists(): write('FINAL_REPORT.json',{'CURRENT_GATE':'ZERO_TO_CAD_LOCAL_PARQUET_NOT_FOUND','PARQUET_PATH':str(P)}); return
 import pyarrow.parquet as pq
 pf=pq.ParquetFile(P); schema=pf.schema_arrow
 cols=[]
 for f in schema: cols.append({'name':f.name,'dtype':str(f.type),'nullable':f.nullable})
 write('PARQUET_SCHEMA_AUDIT.json',{'file_exists':True,'file_size_bytes':P.stat().st_size,'sha256':digest(P.read_bytes()),'row_count':pf.metadata.num_rows,'column_count':len(cols),'columns':cols})
 tab=pf.read_row_group(0); names=tab.column_names; rows=tab.to_pylist(); first=[]
 for i,r in enumerate(rows[:5]): first.append({'row_index':i,'fields':{k:summary(r.get(k)) for k in names}})
 write('PARQUET_FIRST5_STRUCTURE.json',{'rows':first})
 low={n.lower():n for n in names}; find=lambda keys: next((low[k] for k in keys if k in low),None)
 sf=find(['cadquery','cadquery_file','cadquery_code','code','python','script','source']); st=find(['step','step_file','step_bytes','step_data']); op=find(['cadquery_ops_json','operations','ops','operation_list','features']); ident=find(['uuid','id','sample_id'])
 mapping={'CADQUERY_SOURCE_FIELD':sf,'STEP_FIELD':st,'OPS_FIELD':op,'ID_FIELD':ident,'all_columns':names}; write('ZERO_TO_CAD_FIELD_MAPPING.json',mapping)
 allops={x:0 for x in ['EXTRUDE','REVOLVE','FILLET','CHAMFER','UNION','CUT','BOOLEAN','LOFT','SWEEP','SHELL','PATTERN','OTHER']}; types={x:0 for x in ['DIRECT_CONSTRUCTION','BUILDER_WRAPPER','EXPORT_WRAPPER','UNKNOWN']}; candidates=[]
 source_class=[]
 for i,r in enumerate(rows):
  src=r.get(sf) if sf else None; typ,ops,_=classify(src) if src is not None else ('UNKNOWN',[], '')
  types[typ]+=1
  for o in ops: allops['BOOLEAN' if o in ('union','cut') else o.upper()]+=1
  if not ops: allops['OTHER']+=1
  has_step=st is not None and r.get(st) is not None
  source_class.append({'row_index':i,'id':str(r.get(ident)) if ident else None,'classification':typ,'operations':ops,'source_summary':summary(src),'step_summary':summary(r.get(st)) if st else None,'step_available':has_step})
  if has_step and typ=='DIRECT_CONSTRUCTION': candidates.append({'row_index':i,'id':str(r.get(ident)) if ident else None,'operations':ops,'source_summary':summary(src),'step_summary':summary(r.get(st))})
 write('CADQUERY_SOURCE_CLASSIFICATION.jsonl',source_class)
 write('STEP_STORAGE_AUDIT.json',{'field':st,'storage_types':{str(type(r.get(st)).__name__) for r in rows} if st else [],'raw_step_present':sum(bool(r.get(st)) for r in rows) if st else 0})
 write('PARQUET_OPERATION_INVENTORY.json',{**allops,'MULTI_OPERATION_N':sum(len(x['operations'])>=2 for x in source_class),'SOURCE_TYPES':types})
 write('DSL_V2_CANDIDATE_POOL.json',{'count':len(candidates),'candidates':candidates[:10]})
 write('PROVISIONAL_CANARY8.json',{'status':'NOT_FROZEN','count':min(8,len(candidates)),'candidates':candidates[:8]})
 write('CANARY8_SOURCE_AST_AUDIT.jsonl',[]); write('CANARY8_SOURCE_EXECUTION.jsonl',[]); write('CANARY8_PAIR_GEOMETRY.jsonl',[])
 report={'CURRENT_GATE':'ZERO_TO_CAD_PARQUET_SOURCE_NOT_EXPLICIT','PARQUET_PATH':str(P),'ROW_COUNT':pf.metadata.num_rows,'COLUMN_COUNT':len(cols),'CADQUERY_SOURCE_FIELD':sf,'STEP_FIELD':st,'OPS_FIELD':op,'ID_FIELD':ident,'DIRECT_CONSTRUCTION':types['DIRECT_CONSTRUCTION'],'BUILDER_WRAPPER':types['BUILDER_WRAPPER'],'EXPORT_WRAPPER':types['EXPORT_WRAPPER'],'OPAQUE':types['UNKNOWN'],'EXTRUDE':allops['EXTRUDE'],'REVOLVE':allops['REVOLVE'],'FILLET':allops['FILLET'],'CHAMFER':allops['CHAMFER'],'MULTI_OPERATION':sum(len(x['operations'])>=2 for x in source_class),'PROVISIONAL_CANARY_N':min(8,len(candidates)),'AST_PARSE':'NOT_RUN','SOURCE_EXEC':'NOT_RUN','STEP_RELOAD':'NOT_RUN','PAIR_GEOMETRY_VERIFIED':'NOT_RUN','VALID_NATIVE_DSL_V2_CASE':0,'TRAINING_RUN':'NO','DECODE_RUN':'NO','PLACEMENT_CHANGED':'NO','C2_CHANGED':'NO','SONATA_CHANGED':'NO','SPATIALLM_CHANGED':'NO','DSL_V2_CHANGED':'NO','NEXT_STEP':'SOURCE_FORMAT_REAUDIT'}
 write('FINAL_REPORT.json',report); (OUT/'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in report.items())+'\n'); print(json.dumps(report,indent=2))
if __name__=='__main__': main()
