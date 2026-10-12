import json
from pathlib import Path
o=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1v2_size_placement_overfit32_v1')
lines=[json.loads(x) for x in (o/'registry/PARAMETER_FIELD_TOKEN_REGISTRY.jsonl').read_text().splitlines()]
payload='\n'.join(json.dumps({'response_sha256':x['response_sha256'],'size_spans':x['size_spans'],'placement_spans':x['placement_spans']}) for x in lines)+'\n'
(o/'implementation').mkdir(exist_ok=True)
(o/'implementation/TRAIN_SIZE_TOKEN_MASK_REGISTRY.jsonl').write_text(payload)
(o/'implementation/VAL_SIZE_TOKEN_MASK_REGISTRY.jsonl').write_text(payload)
