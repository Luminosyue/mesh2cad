#!/usr/bin/env python3
import json,sys
from pathlib import Path
p=Path(sys.argv[1])
try:
 try:
  from OCC.Core.IFSelect import IFSelect_RetDone
  from OCC.Core.STEPControl import STEPControl_Reader
 except ModuleNotFoundError:
  from OCP.IFSelect import IFSelect_RetDone
  from OCP.STEPControl import STEPControl_Reader
 r=STEPControl_Reader();status=r.ReadFile(str(p));ok=status==IFSelect_RetDone
 if ok:r.TransferRoots();shape=r.OneShape();ok=shape is not None and not shape.IsNull()
 print(json.dumps({'step_reload':bool(ok)}))
except Exception as e:print(json.dumps({'step_reload':False,'error':f'{type(e).__name__}: {e}'}))
