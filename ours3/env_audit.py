import importlib.util
for x in ['bitsandbytes','deepspeed','accelerate']:
    print(x, bool(importlib.util.find_spec(x)))
    if importlib.util.find_spec(x):
        try:
            m=__import__(x); print('version',getattr(m,'__version__','unknown'))
        except Exception as e: print('error',type(e).__name__,str(e)[:200])
import torch, transformers
print('torch',torch.__version__,'transformers',transformers.__version__)
