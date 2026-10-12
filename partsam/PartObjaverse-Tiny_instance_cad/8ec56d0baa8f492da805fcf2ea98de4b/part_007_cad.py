"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_007'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ec56d0baa8f492da805fcf2ea98de4b/part_007.stl', 'relative_path': '8ec56d0baa8f492da805fcf2ea98de4b/part_007.stl', 'source_sha256': '6ebad180cc36262a0a2baeb65ca03b58f2c70d165776b1e6b57843511c5204c1', 'input_faces': 150, 'input_vertices': 107, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.10703419148921967, -0.1438845992088318, -0.2921278476715088], [0.2058829367160797, -0.12007734179496765, -0.1901865005493164]]}
GEOMETRY_BASE85 = 'c$}q}2~1UY7RE0it1N=J6c;WoKoJoI6ma3GY$E~>1X)CQ2#<=iC`+l1*xb=L#cFV=yJ`DcO|fGaYqjlYk^7vAV(Zq_L^I9gwN#Qi+K9H*rp`F;p6~07PG*v3<|Y4pKR(Vo|8vhhcgZtnxeW+b@Cj4)S}NV!d=$l4zDlstVr^`$t+F=7)UR0Oq6`w>`23<T<rHR{OI(x|WpzZgwW+ExB3X@?QIi-Etwz)=Z)|R?tgl$!SZy`@^vb83tWLjaY2^y5^Y6&XvD2c}xF@64HR}KPF{;pa)tpFis_mmQdY4nRVMU)Cs(7pvUuiFe|K$SlO&@1<8ov7DNV~)(9TDFWQYyZdeOTg^{qKlxyWy)#e8oD6SKsUFk$fWq#8-X@5Z{(}8~&%G#dp~I#n-y}#aHZ+;%oh<CBMz?bx!t;Fd<J{^eN+S-F>+Drj$1EEf+M@bG}%7{m{$EZ;e8HP$T@-MRv*m*AWu$c+dM&`Cd#leAlm~9)0{1;ybQw6kpjMfjXxZOPwaKcJWQ$>=obCkR!fr*z4jua=oyx74eRb4j}*eFJ)g#+H&zNtvcd2&z5*wVJq^d4m>6OY}<i4dyk-RAB2jp_0EuZ)24IS_qIiR%dz#Szy7Y&uT8Ik|I~^uiO+^_D()9wxgCu@d(D;psHykG*LU8=arqUX&v*VVzUilh@V_{57X5#SI{VIGPJVktd}WI7pQO%vlci3}j+5f+odM$8b`C_IRaf9&3>DvUe5u4M`@Rw1@tH+@$B7IaS4ZDx;y<W^zwy>d$#d+M_<Cuh_{!6E%=3DG^lf#k_<Bnv`kWStd3($A6FDx+7S!{xhxA8((_ehshc8Os^d&ChTUO<X@7NlP<2`WyynN5MTzsvnQ|eK=T`owSsa43+9Ejt(vI+GJtr6dnQy_Kf>soN$M>HV6Zw2yu6{DX$&4_;{7;_liEWV~a3qSBO=D*~Ri0}73E&KkMEAftw%b15(L&Vq9T;;gb+)J2;m8$s4`<dv&gP4m_*AElnw|pnZrHx4xUpv?$zT?{OQGdkeIFB3J;Mc#6I!gm(ezcz5@N+L=4tKiZdMy64_}bwYaJ+p<m*oHcH{lmHO1$lb6!Degci?*`B7d)4&bu<wty|9H&lfQdzVvr&5nrEk9rLs2s^rn`yehsUX&Lg2J|^`j8}=i<Fc0-OuFLt=(hiDmiyehN$M;Geefv?wuW^$)E$N6iz5XHU$(SR)_F4yyH=zsrzA{AenBJX=IgAQBBk{E{r?6kaW%>V(sp4xlwxRy2@zQ_gZ^`fr*5ZEByF}vkt(oHM4V$p<jYyoYH|oW=d_76>J0jbW-`Xm^Z7ZG&%KUxEW8Z*0p6G*?w+VCduw8s*`1kNnz9#YN8=J*fcLbu&wQnNNy<Ir2INq0P4~egMA3%QH5A!hjdCX^-9r+L6Mf|~d^m*@9__HQr-tJ5nU)|O(zN2k7uG6$m^mBRmS&1K4hv!cDA(;nT-DL6gD=D~tmLEm_GSk^d&zDm9io~mLXNs>T<36mp+cBSenvj3vTwK>HZ;5XySR=mnKJN3{*q<@C_ctT{0iGik7jN|8=r-{k>E5_c7Cb~f<6lC&{T*D7t^G1r`pG@0vuPjZa|QC4cE2UQZQ=#g@Aoa@>-tdt;U(zLU)JJ&{_RclAu0&-Fli>{%EP-y_VqDiJ{wH%O$p-bWw?K;TU7KR+bq7e?l{g%Tm+8y$}{4dDsVq{%qzlmx9wTvG4Db>-|xrscXccF9qW$s9#nxogl!Yw5`yQ5l3+z1kL}_+I`Z+pQML?z$jivH<uv+ss}6IL*MT~3cA;-y`Qy3{|3rLScM$5o`;(k^t)vI_cQ3-e1FCQx{q7p_bcW+PU0NgedDZ7S{KdGAbe-|v-4kD3|2*d5xiX1Y{-B<d_>0T%o^W-Q#G4`$#J6O7qfXD~kSAlF_<DOh<~FAd@zwd~Ft<gx9^==+uP8;HuX>Ot?!}8;=EvS*k9|>{)#mAZqjD~9=UZ$|<)g2#o(TIz|MM$sZTzo$g-wY4e_vrEoHax`*9b0yL#a=aL&@RP7;-o{mO7mrOHQW#hMY`Jrxuda$@8g;$n(hs)Jk#zxrk~d7m-V-)#MU#8TBc08M&NVOEz>Fxtv@<T}rMXFXl41lv+bBB^OhdkPWRO7n2uKE#!sdeCj-MK6x6K!Ew|%WJ9Nt<H%9eN#rPU7?;7rsN>1Q$b+dWc`!MUI+7en4xomR1IYf=C&>O}Kk9I@A9)aU1bGlSh#E=`A`hj8lZTSWP-Dqs$P=i^<O$?>YC1WdoJ5^ZP9mpJ3&<(tOllE1lblU0A!n0wsb%C`vYA>=Hnf6lCNH2aCNCi8aT%OLEhXoWv#7;nLl=^>$Qjgpat3)ObsBjlIhxDhvD7%Sp;6?q<WbZx@+fjJm%+Z&VPs#j4|OovhwMcSBzuuPr~zaT@&Kwoc>vj+>PL1bdr}9HJ;~nGAhI`kAay8tAbALN40#B7G<5=bG<h5~o;;2`k(xxFNS;DXAx|MEQZvbk<XO~g@+|UfYA$&;IhATA8@hm;N=~EZk<-X?xePW@bI2z03~CnH&<yenasqWGIe|Qx8clX{E?4Jrp(<o^mWyk!+kg8h>R%tt2!8B`sek|G<B$JGzuE1~_0N|9bC$a?cg`YQl?JD7FeXF!2fd0Z`2'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
