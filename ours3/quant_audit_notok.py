import json, os, ast, re, csv, hashlib, subprocess, sys, statistics
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
SRC=ROOT/'p1_cadquery_tank_airplane54_full_v1'
OUT=ROOT/'quantized_cad_representation_audit_v1'
for d in ['original','parsed','quantized','dequantized_cadquery','step','metrics','token_stats','quantization_visual_comparison']:(OUT/d).mkdir(parents=True,exist_ok=True)
parts=json.load(open(SRC/'data/parts.json'))
rows=[]; params=[]
num_re=re.compile(r'(?<![A-Za-z_])[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?')
size_names={'radius','diameter','width','height','depth','distance','offset','thickness','fillet','chamfer','extrude','length','size'}
angle_names={'angle','rotation','revolve'}
dir_names={'normal','xdir','axis','direction','vector'}
def classify(parent, val):
 s=ast.unparse(parent).lower() if parent else ''
 if any(x in s for x in ['spline','lineto','moveto','threepointarc','polyline','origin','translate']): return 'CONTINUOUS','coordinate'
 if any(x in s for x in size_names): return 'SIZE','length'
 if any(x in s for x in angle_names): return 'ANGLE','angle'
 if any(x in s for x in dir_names): return 'DIRECTION','component'
 return 'DISCRETE','literal'
for p in parts:
 pid=p['part']; folder=Path(p['folder']); src=folder/'target.py'; txt=src.read_text(errors='ignore')
 h=hashlib.sha256(src.read_bytes()).hexdigest(); (OUT/'original'/f'{pid}.py').write_bytes(src.read_bytes())
 try: tree=ast.parse(txt); parse=True; err=''
 except Exception as e: tree=None; parse=False; err=str(e)
 nums=[]; floats=0; cont=0; disc=0; spline_pts=0
 if tree:
  for n in ast.walk(tree):
   if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)) and not isinstance(n.value,bool):
    nums.append(n.value); floats+=isinstance(n.value,float)
    par=None
    # infer call context from source segment
    seg=ast.get_source_segment(txt,n) or ''
    low=txt[max(0,n.col_offset-80):min(len(txt),n.col_offset+80)].lower()
    typ,sub=classify(None, n.value) if low else ('DISCRETE','literal')
    if typ=='DISCRETE' and isinstance(n.value,float): typ='CONTINUOUS'; sub='coordinate'
    if typ=='CONTINUOUS': cont+=1
    elif typ=='DISCRETE': disc+=1
    params.append({'FILE':str(src),'PART_ID':pid,'PARAM_TYPE':typ,'PARAM_SUBTYPE':sub,'VALUE':n.value,'LINE':getattr(n,'lineno',None),'FUNCTION_OR_OPERATION':low[:120]})
  for n in ast.walk(tree):
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr.lower()=='spline':
    if n.args and isinstance(n.args[0],(ast.List,ast.Tuple)): spline_pts+=len(n.args[0].elts)
 rawtok=None
 rawtok=-1
 rows.append({'PART_ID':pid,'CASE':p['case'],'FILE':str(src),'SHA256':h,'PARSE_PASS':parse,'PARSE_ERROR':err,'LINE_COUNT':txt.count('\n')+1,'CHAR_COUNT':len(txt),'RAW_TOKEN_COUNT':rawtok,'NUMERIC_LITERAL_COUNT':len(nums),'FLOAT_LITERAL_COUNT':floats,'SPLINE_POINT_COUNT':spline_pts,'BLOCK_COUNT':p.get('blocks'),'TARGET_TOKENS':p.get('full_target_tokens')})
with open(OUT/'parsed'/'parameter_audit.csv','w',newline='') as f: csv.DictWriter(f,fieldnames=['FILE','PART_ID','PARAM_TYPE','PARAM_SUBTYPE','VALUE','LINE','FUNCTION_OR_OPERATION']).writeheader(); csv.DictWriter(f,fieldnames=['FILE','PART_ID','PARAM_TYPE','PARAM_SUBTYPE','VALUE','LINE','FUNCTION_OR_OPERATION']).writerows(params)
with open(OUT/'token_stats'/'raw_cadquery_token_stats.csv','w',newline='') as f: csv.DictWriter(f,fieldnames=rows[0].keys()).writeheader(); csv.DictWriter(f,fieldnames=rows[0].keys()).writerows(rows)
json.dump({'TOTAL_CAD_N':len(rows),'ORIGINAL_GT_VALID_N':sum(r['PARSE_PASS'] for r in rows),'TOTAL_RAW_TOKEN_N':sum(max(0,r['RAW_TOKEN_COUNT']) for r in rows),'CONTINUOUS_PARAM_N':sum(r['PARAM_TYPE']=='CONTINUOUS' for r in params),'DISCRETE_PARAM_N':sum(r['PARAM_TYPE']=='DISCRETE' for r in params),'SPLINE_POINT_N':sum(r['SPLINE_POINT_COUNT'] for r in rows),'rows':rows},open(OUT/'parsed'/'freeze_summary.json','w'),indent=2)
print('DONE',len(rows),sum(r['PARSE_PASS'] for r in rows),'tokens',sum(max(0,r['RAW_TOKEN_COUNT']) for r in rows))
PY

