import json,re
from pathlib import Path
import generated_gate as G
base=G.E/'compiler_smoke';source=(G.O/'objects/pottery_large/cad_parts/PART_000/compact_ir_v3.v3').read_text()
cases={'operation_header':source.replace('\nO R\n','\nO E\n'),'q_out_of_range':re.sub(r'(?m)^(Q )\d+',r'\g<1>16384',source,count=1)}
results=[]
for name,text in cases.items():
 assert text!=source
 p=base/(name+'.v3');p.write_text(text);r=G.compile_part('pottery_large','PART_000',p,base/name)
 assert not r['PASS'] and not (base/name/'part.step').exists();results.append(dict(name=name,rejected=True,error=r['error'].splitlines()[-1]))
(base/'NEGATIVE_INPUT_GUARDS.json').write_text(json.dumps(results,indent=2)+'\n')
