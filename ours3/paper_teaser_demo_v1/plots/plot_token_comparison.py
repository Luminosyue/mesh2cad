#!/usr/bin/env python3
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent
rows=list(csv.DictReader((p.parent/"tables/token_comparison.csv").open()))
labels=[r["CASE_LABEL"] for r in rows]
raw=[int(r["RAW_TOKEN_N"]) for r in rows]
compact=[int(r["COMPACT_TOKEN_N"]) for r in rows]
x=range(len(rows)); w=.34
fig,ax=plt.subplots(figsize=(7.2,4.6))
ax.bar([i-w/2 for i in x],raw,w,label="Raw CadQuery",color="#8b9aaa")
ax.bar([i+w/2 for i in x],compact,w,label="14-bit Compact IR",color="#16818d")
for i,(a,b) in enumerate(zip(raw,compact)):
 ax.text(i-w/2,a+max(raw)*.02,f"{a:,}",ha="center",fontsize=9)
 ax.text(i+w/2,b+max(raw)*.02,f"{b:,}",ha="center",fontsize=9)
ax.set_xticks(list(x),labels); ax.set_ylabel("Tokens"); ax.set_title("Full-program representation length")
ax.legend(frameon=False); ax.spines[["top","right"]].set_visible(False); fig.tight_layout()
for ext in ("svg","pdf","png"): fig.savefig(p/f"token_comparison.{ext}",dpi=240)
