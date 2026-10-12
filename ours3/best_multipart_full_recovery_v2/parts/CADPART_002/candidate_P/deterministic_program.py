#!/usr/bin/env python3
from pathlib import Path
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox,BRepPrimAPI_MakeCylinder
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs,STEPControl_Writer
from OCP.gp import gp_Ax2,gp_Dir,gp_Pnt
OUTPUT=Path(__file__).with_name('candidate.step');KIND='BOX';DIMS=[42.28161973949962, 45.38436614049478, 71.15091028176535]
def build():
 if KIND=='CYLINDER': shape=BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,-DIMS[2]/2),gp_Dir(0,0,1)),DIMS[0],DIMS[2]).Shape()
 else: shape=BRepPrimAPI_MakeBox(gp_Pnt(-DIMS[0]/2,-DIMS[1]/2,-DIMS[2]/2),DIMS[0],DIMS[1],DIMS[2]).Shape()
 if not BRepCheck_Analyzer(shape).IsValid():raise RuntimeError('invalid primitive')
 wr=STEPControl_Writer();wr.Transfer(shape,STEPControl_AsIs);st=wr.Write(str(OUTPUT))
 if st!=IFSelect_RetDone:raise RuntimeError(f'STEP write {st}')
if __name__=='__main__':build();print(OUTPUT)
