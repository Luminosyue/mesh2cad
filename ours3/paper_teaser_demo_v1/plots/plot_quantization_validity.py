#!/usr/bin/env python3
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
p=Path(__file__).resolve().parent
rows=list(csv.DictReader((p.parent/"tables/quantization_validity.csv").open()))
x=[int(r["BIT"]) for r in rows]; y=[int(r["VALID_N"]) for r in rows]
fig,ax=plt.subplots(figsize=(7.2,4.6)); ax.plot(x,y,"o-",lw=2.4,color="#16818d")
ax.axvline(14,color="#dc7b30",ls="--",lw=1.5); ax.text(14.1,5,"14-bit plateau start",color="#b65e1d",fontsize=9)
for a,b in zip(x,y): ax.text(a,b+1.2,f"{b}/54",ha="center",fontsize=9)
ax.set_xticks(x); ax.set_ylim(0,54); ax.set_xlabel("Quantization precision (bits)"); ax.set_ylabel("Valid CAD programs")
ax.set_title("Quantized CAD execution validity"); ax.spines[["top","right"]].set_visible(False); fig.tight_layout()
for ext in ("svg","pdf","png"): fig.savefig(p/f"quantization_validity.{ext}",dpi=240)
