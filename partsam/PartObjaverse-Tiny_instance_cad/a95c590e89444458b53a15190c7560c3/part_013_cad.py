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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/a95c590e89444458b53a15190c7560c3/part_013.stl', 'relative_path': 'a95c590e89444458b53a15190c7560c3/part_013.stl', 'source_sha256': 'c0edf04770f135fa8135566e298a11df689e555e486baceef02bb486498e6ca9', 'input_faces': 300, 'input_vertices': 152, 'input_watertight': True, 'input_winding_consistent': True, 'input_bounds': [[-0.07940828800201416, -0.262686163187027, -0.10922539234161377], [0.12119722366333008, 0.12917256355285645, 0.10080400109291077]]}
GEOMETRY_BASE85 = 'c$}q~c~Di?0f#T3D6XieC@#3-f{G}LM10SU7>$a83%Ie1h=72Kfcg{{L=Y5}w9&XP(YPxrZq%A+>)OdoHDl7)I+?bPZBvu_N0Mp!&N<)hyZ64f(`nz#neRKlIq!1bz2}^J&JaDxtAU@UKHaq2_V$JKEi_G(W}2V2JT*6eQF3bDz^t5=9-6Pr#YboLlo^ww<2<zGT2W9+YF=_~P()zR$h7dF;J~1??A-j^#H<C`xhbh4k4ntUOLgXX>4`b1&U&B0VWGi+L;3~>t_u7gKTSj*I>uhODHs@5XcO%7X1C3l*MGlN*6ZFoAnT8gpO<WqxJTv%{r1|7d4bPCS?_#spRBj5JSX`yphhzEgIzXbu2oe?<`y0_wLjy1TDGh9-EV4tZP!^@f4%g5S-;!ilw^F}Ny*z0Wj13TGT^xCZ|y--`+$q*WxLf6_L|zCDY_`@f4;gy*29B7l>B__1IfAm<;J}J$4~Cd`l*0Zru<KrK9TkGpB5T(d#kTMmi0!Ns$T_lM<lcF{an&MBj1?Yzw%YNf9qrFdRGps-<hkPk7Hi0&6rPUr}A@OsOR--AC+qr<7L0R_gt_U^Queoc{nmo*2?;;h(nSiV^sd)Q`KJ2<ExIyd~DoBS-<~G{hh$4dnEr5aL#7TbJ{y3cMh&KwJ$q%Lbf~n!v$0OhvVgQaXg7u<LPya{eq5BD<8{xv`>vO4{RE&^4cWz{4X?A{aBs&k>rBJk8H+#$JC?pdXdE!OzkH}$$r=SRG%}oZ~m%Q*0c7VR=?-fF3D*j57qpbTw^oj_AR~ScyPp|TsF41C&k^7_1N<t7~9wHo+8JCV@<ibKjD9@mhE3A-d6YPhMH&OT1Me5*}lyU`hR-6tbg;Vsz;`%`A4o@ey!%s%I9Y#6TG*|>)-rqy{!N6-6m6hs9fdRrTxZSOUbz=*|Xz1Q$Fy>Rmpp!)O^qRe6t$A&mKwcex=6A*N<c#`1+E1UU#>yko~L=OH%Xtmvyo}@lcg1PoHvC)}MEsY09&{yD95_+119}(cD(A?$`YsN&D_;@;)~i_cQsu*}o|=<+CHy@7+B3#7#r)_}=fjx(|;_jP11=5A}Ovuc&q5aZ`1@UJ0uInLnuYQ_r<4s{i$0ZZNffQmOhMerK<-y(2DP^*?x`nm6G|J4JopXOGl<EB%YQKjhkz=_<D`J7jF{ICetbe@E5n%f?*GTcXBo@tp(4>p1rP{+`T3-&{4ew@<E7<2I`Bi0SX1^HuBEgHCm(zuWD7HEyqOIBaU4VVC1pv$Zny$B~k(o{N8WxvBk+9o2Iw`PC^?|4+xL=kjgPHdFf-w^To-#+@{^-*!}uzZo|_H2vOZYt_7{>Uh!A{z#GhzT<DUbEfNOg{gJAWQ+NJjtZ0G-tqj4T2uR+ua?QY;v3Wb(Hxr=%lgYJS4{2K@0a7)G4Y`}_bdL1%&*-wJs0PCa8&YmjQRR=7aSL?-*dx!oe@{$d($!XfVrP(FV%YcxV8CrZCi0k=EYy0H{~hA)j03<bf4)uw|=X}dE?khQ~P!c)i^JUG>^CLUDP-aJg~`how`z$KR>J1k>_3q{^k7AbL;%lbL;#fcbi`kujM#(TOah?x;~J*tq<gG>qBj+nm5+<P0y|Co1R<OH*&Z2ZRTh4J?gfulDn<Lk6+05q1*be=hpR~+-?2WbL;v)^!h2;PwV@L-0gkzCQk12+}?NOZtuI{nP+5fegBfXy?^!G`u-(%d;fO)R_!mX`v*O@?jQ8rx_{7f>;9p4gqm;G{S3L=e#Wz_+8<f>S9)&UU+KAZf2HTv{nhq|D!1<U^xV4NdvCbfA6xg6dT!lMCRD22x?k0E>wfiROLf1j`(bjo{qTe+xlXz5&&l2P=X!44pOd@o&o$Oj>-j>@t>+6px1KNb+<LyaHTt@&ThB*&Zap9Ax%GUc=hpL4@w^+dZauH*x%Iqu*ITVS*7KmA8_$E$rql1ochCN=%6YOC#m9O2O-nQ!eXBU~R{h7L@1mjq)zNoINXY+t^d0N$!+2-uO%Xm6zKsvXhrxI7VR#=n3Gah<fs^qrxIdhV`{RBv8u!E7IZH<v1EcX6d^JV515U*q_&PWlUxydNNq8~79KM4u$Ftzucov=n$Ky$O0vwAc;5iiGqbb6B!rpjKyah$LFC2>d;{D(-ydNG6`{2QNYuE*EjW>q=cw@W)^urtA8f>SzKEgc>&(D)0+?ygikRm)5#^AAd0bGq2;9Duew?hZM9p3@h;XCkMuo&NkSHb0Y6<!Xr@N#@TOv2aWnJ@v*#4}(Ho`G+q2+xP3@qFAy5#Am4#Jl6oU<<q%-kc)5CG^Ex;;mpmycOOb2IKwl0kAbb0B-{u<85#s*Z}vz8$u0lh<iX!+ynQ5-nbXu$XS}gCeRxf48)t@;S}MsU@Sfhp9>4{xp)fPil^YI6ycR{J6?%b!yR}vz7y`kcj7g$3a`Pp!E$^XUIEwR75E02iEqG{zzlo|z8G%A7vr0pWeY5W8*#yWybRBUHar&}NfAB>cE<<donSM(6W$p%$2;Q#DZ+cemUs`m7i@+1!h>LcJO~ei1Mo0>IBbIt$NNGbyf5ArHpIK)9iRu^0dEVv@V0n+*a&Zr2WYN25I_;$%~?jk!LTVl7!QF>aKUgq1dpHykAt)DID9^wi_gc?U<#gwFNCT1LVN*5_&ivN&%;;3YJ4TW2JXby;A>$Gz7{Wm+wc;66|BHl;Va+<d<C8jm*ClWGF*%&<B4z+o`^5iTytzGMffsjS>!Bv&Qe4Xz8NmVm(hMRMR+MJ!v%BkQal}w#MALeI0zT)gbQ}Y1qb4h_$b%|ABEdtFWiogfkF5fd>jnJ$Kg?MI39&hfPL`^_(a$hpNPK;JK*o)Q(#+s3O)_C$EV@bVE{fIp8>n!Gw_+3Yktn82%qgNbKqNW1pXF21P;cB;Gr-C7mUC|@pu@A3(m&{({RCsxZnaj6zYFB-q5#r`W{dFIdC362cHdB;<NFYaE;-ftl^#st~K1lwcKOD62m<&;h6}oGCZSIJVU`1hG)8hXD*nnxyFF-i7;7njTzw+V4~(4W5T20Qq46cg^z>FG}jmwJ_hD#t}!p%4i{;zIU-!2N5Ugvk>;9r!VBSMT(A@uOvlstj_~M79-e+)|L$M8u8%`*%#8oowSLol3^soA@6P0(hvMi-4aL69xta5nH|7^&1=0Qi-ylkD'

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
