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

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5c3ec179b3fb4fb1b006ff935d5dfb77/part_005.stl', 'relative_path': '5c3ec179b3fb4fb1b006ff935d5dfb77/part_005.stl', 'source_sha256': '606faf6de94ce47eab8ab93a40dd2ec45b59821cb6f04d2f3e44a0e04b83512c', 'input_faces': 228, 'input_vertices': 245, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-36.88883972167969, 2.0520782470703125, 8.71784782409668], [-9.79958438873291, 70.36659240722656, 19.948379516601562]]}
GEOMETRY_BASE85 = 'c$}r02~<=^*2fDFH&(Tyh+DHL;DQSv3~mq9xGU}(Y8%8T0wOpHCef#HM^KCl3TjK-!6h0ADv}q228}VqJ#J~&;3RR}VlbJ=RNen|CYdweIp6udKIebxy<gpT>(;GX)sNPweh$@40v|7t_jaq|)CNK*ISZ4R6`MSBYD{cOU}935op2|vKCjyk1`Zz(HQG+h67Tp;icN`0_6s-rb)FpN*V^nid3y59<cWzBrYBE|Rs79~@hP#Ar%aic6f5ujI|PTcHU|Z?Hos^7KYnV<5cHEXA`RJUv(^vRRQq#DE7j_G;MShjD7yc+wI8)@z-<98u+M7LTD2B;_7gppxbA<uxoVBdB=DK=uX|^cAMFR`+I8|TeyiO=wYJ-PBNW%i!(JRbP4Q?`nE$$k?6n|o@?#wgZjL^LIIH}~-WCCF8Bhb`PWGXAY^4RnwPcRJMF7RGuLif3MZ-Sg2HA^vaPugRe@HHkYa0SCZhVVzPdZTi;`Bp}{14*zeXk?_0C3|h;ukq}$dAPdTt9vg^V$_k_U1bk#BEFMFs>z#;xYFHw=_ol#)vKyztzP2!5GXd@d(-LUwse%-4Tz`Y&-H+3@+|pLHrjg$=;gZoVd9Y+aLWq#bYV<h5g;15&xjR$mfU5cYj3O@P8Bb>EK$^Jn;QtG_J_@fxX6g&asjoOBlEo%;Waof&2t9H($cIO&?%hZtlp>>pYwqNqG=UzUxZyzXaDElZYGV4dP<c0mQRwH0s<B+_G>r?E4)jE^<p?pNTldrFT)!Yr&1~n3wR|jD67v+*<D?{JV5SocYIzYg@~)z9FT=wRmuIE8cf!t;kPV2K-0205921@oTnl_}SJSJfZ?|whrq;an9I}afb~=y*&ygZd`4Q{EV9mKMz8P>lx$W=gD})Ss4sJ8D|k^ot@x6f}4w7;ipqW#D9u8=RwOlg!oT_>z+KXs^!@4SAvLZ=PFQd&TX;pj)RM9z2JYw4-~&~2;Atn4t^YVw<P~d|I(S(YyTbiDUHCq!izdl{=ck^^{ROi>)z!MaV>Q(*6Uh0^44=NaWTt+aTj;Ne5)4_H;P809zq-u=goZhiAP<DfscKOmofL?x_yyC^EHaV^`B2++{|3mk3ZX2ZAJXa2T?zsyNTOgVZOR`JI&YF8H9K?-a?+e$6{UuEyBsZkk7ZDUVyJ|PFyz^pdNDipw3;uh3iDvx2lJDj`<MRZee}3g3oDQ;;1+5f9L#XC14#*;I_e~h-c3loRhV{tpm9ph8=_b3orOd7!5x&ys%yi!1XaV5a**<#2;*i{R19%_;RfKl}%w}A0&udyyMys-vurML7tN*VZM#oJ{|KlzPgX~3fM^8dd3<4>t|xVuQm`je!;lnVm#u{Vczuw;(Rt6b<zji_5q(`b&C;yX*R|+ArHDZh4mc@ZeDN|aaNy)^J?lk_^;q~&&{Cu>L=a^CI7Cxe=9pvoZ3d_jbmVMIt^|H7w*V|wrm{oaIr3NV=2e^#F_GD)T;wOPQQ`8b<s59`ls&j^CRLhipC=kHNcH)C5V4#8qR_9ZtxR&0ps>Qfc4D>x0tye8Wq9M2QIL`%Xu!(#`^kag;3rmx?^3=Z1z#DB{LJe{Uq4m+=TVokxty0fpg5<br8j`U0zDu)@ldxANdsdTn%o0QVaDnW)Jdka|v;CEdy}|hG2cKgNwv7Soe)LF)wd$+kIZIJDi{Oi-}wEcwgVk$9Y(_2>c<>x9th+>p<6Fia!SHsO9vadD)IS5x1PP=lUE%d64H2?62ay5{2^+e_mCP;#yBHtk+=AKzgn}xFusd=5_fl@?7x>`~b&4>>lE|0&Y9casD<O=U5uJR-M<eKECgakN!bipIeN2=;Md;WcOp@)|5|?w=sD*KkZg_p!gTyd^Uclpg6^gbmHbgCy}@KO{l{`OTevMw}0!6d6h4MpKH8cAss1i#+RwYg&WuH0GwCGq1nWBd;UJ^BXIt|oCW_!auEO5Yp{+7z_myGo>qeV*d|OPZf%EiQeSY<o9rLQ5x3orMczI;OY5a2mIP8fFJ?6%?t2#RjkAw{-^lbJyA$VdK8)K7ZsgUYxRadyRcrQ`58g71?2W=qipP930es_jve(>J5Z49{1<xMsLgNm0B|o-T0pO2UI+NYUu(ytF0$#Ba{(tX>_rM?r@Lk#DUo>itbN)zS8{)nRu4G^D9_8QSumk+Zwd7x{`<>R^JYXyMTjeIQcMiq5owXUfEV3Hi_jaQ=Et^(>XJ?UrTkUt-5_e7mcV0;LM#6E_Th}D;Q7b9WdOi5JjEn=1pGSVo+RJv-emE3-=}U@7TU-hI%4Y1ppCiSSn~r?OI)ax>CwqNH3dN&eeA$}#HhapmzB>%(lJ*?@Kq}(tR7~|?q&x*5wF-G2Ujm+X7kmZQQ5-u%-0FRq{acaG{Mj8So*ISV!y;=Cf0;n>i1~-XuVz;#yJwX+uM%>=Jx?S5!mT~EW7dO5HzPlKmnW1T?MVjst>v({pFsAOUdzGTt*eXq1W`Q3-gm&0z92uwlyhXS?U(~zQB|M(e>{lxukF@o@cymbX`VyxkRP)#0K7+C@^7)0VZQHo0q=dSCiw|kfphY42zY_0P4i#Ao9wNQ9^lEoo^+pPqH&EqZs2DM-=O;~ZkTV)ovnzQCfbpo%bT$7Wpltww-PtHI-pL9l9@Z$Q#=imkbjRD@QZbbi>J@Yzur3peAGdz2Xm4?&aqz`fS1LSe?1!eRQNN$W>DU=HP=zM8(hHS4fy}M9nII$(FxpjHu=|%_4lTBlOwo&2I?&`in#9duqE-yxi~l4jUsMz{tUdJobqYgcsz*stbFhlYsrtbtBK}o6zu}Pv6$i%pF~qU`iphoXSQL#1WzMB+Ret`q7Us~J#Hv*>soj4G42hBUuciIvV0mq+!yDb2!8HGt>0mP;+lsW-JgCM1il&EV>8Z&(2m6Q%uV3ivdNDn-3Rf{XFe(oc{^T?_lF7Vz)Ra=UH0M}*19qGUnPjgypQ*ag-gLV)<m4WexmxfUeUpm=EBdjPN?UzDc~ipsKeY<h(GCV@Q!mRpGFSXe`yDB=Xo@)_0i9$+brfqb~raewjn<c0>JlNp?qpizmUCcnh(#*<UsxduHt<-)dhU=QhXoT%^^S5Dktz?XHtHQWz&h<(rSU5GAJJ7<O96-4q?744sm8DwuQete#BQiq;t$@_zH1Gwgs<WjB_Uc0&$C}HF$V5#cyqL5%XQ-1l|<&pwIn=?2Y-=!SCeZoOyX4=ha97o*O~_&ELeJ-ZHMXAijDA&CBvA2j558=fSsiqw`aAtq=PF2f*X^<6N!#2<LX+W#I2x==`@ieu8z}(h|J%0_9md^d_yNE%8}%;=MiT`$apk0N=CczF_V{^&p~$U?2IGfJcRrAALT~bHjcW_=7-NcfESFH}bg>Jn0`~FLu6%bF6bZxR{H5_wX0IhqRvw-W2OAf_su5+ocq6>mua2d<1dr(RA=!_}Bfb;hf(-mF@QsH%F%8`*A~maFadGhhrwJV`VUSXFFP7TUA}u$+$M)h39F#Y{kFA{v%ItkF_{I`&zMHJ*$IPG^TUjHlqsf!!C~CmJzk+`JIzc4=um<C0?0M=Y~<#gYqowZ-d8eu0!`d_F!J8zXA{b3EykG*B~B;li=0LiEC>XBF{cYz)M$v?~BKKi^C3Z>o|PRPRBZ0VpoD!tfTi6i}f&#tA{TD-}jL6W(iEjd$KtJJaP}>bhwXr`ox0Q%%pi~rE&QCWlKl)f0^pj+@c2jA8ZMJuOr@D8dc%_Gt~=x$}yZ{?{q^x4|{@VN8x?uVIu0Vo&$LJP<)Rp>xTKxyXQmvaVG6|y&>w*mj5kyWl!R^c{9o0dg&5)^fSDV+2ij}i%|$(7w^NOmkZtx7as<<WIItD%bw%!=$m=qqjq9nv|EJt<d_ZMVXJYz?OW1Pi~7^A_FsQK&as`7e6x|NB}`)S#6SFGub}$8ZvXpF_EUrZcR$&82>bv3WM3g;cp~*Tsn4XoP&wfClGJ6XkGN0q<5DN3&a+CHeJXWU>T9V&ZZAsBms%;cN@_Q^>V6LQy`yp~mB~CqDpzU&YZbFy+^_8RFjIYL{Jiovmwl?|mPl=vS|s(pRJzKw)H12nQfsBMr8Y@rN$uzBovN0ku1l3m-IBU5^&PV^=Bh1`Dw2B0&nUaSQahy9vDPzN&tt2xilxp;9pM;0<Z(adXO-Uqsl!s+q_#?ZE|tgEpGckH`(l3nnA8CtOI`1iIx2OLuk(41YRp4Y52S8NU6cBW+i#^FbDv_*`TiOAo#Gs*=g#mmPuceG%zu=+A@w~!bDjMt{sa3`&phI1zUTa%;`x_wdxqzKRqCG9UCzNb%q}p0eScf(3g_hl^Us+T^E&O|9I5qJHSq!Gz4#A#d7Y<Qyhc}e?Z4!EW%Cv1HJjITEzjjP$9ae6c#qq=e0`h!Ug76Y^BSqRwg}XVTDvliSFsIJE2I`my({$|$72(yL)EvO`%m-pM|nP9a=hPhpNe}k`z+ubD1Y;$ma_llJnkBfXEXOHzL>{(pXa@T**3N-;GE`hj@7kQpk~)HSGB5YG)JH=Hwx^#e7@eted=268MR-WrK$;hJfs>*c}v+z)sU(wl_E7wDo!e1>aS9>q}-+4_!+ZQbE!sB{iGtK-jsSvYJ}7n_Mz@4F;jL?Qk|s2qyqVw2)=L6tU1Tx#$$Gs>Mk`<YP3|0)Oc=Hd{h6>H&m*PRJc?yE1aMA=01NZ6X&8j&q3Y0N;Q*eD%FJZquRQh7xizl_N?0cY;EpW&-zIDN;T#=cu9G(ytuz1_ba=}QnRI!rTR+smx`1cEHzfj!Zrzf-Ix1DN`*@OMXD8FYy7MlqcwB2j;T_ytW+K^fyewSuSp-NZrt`|UuxZ=rG{`jmdBpPzM{FE%zY!+whwCv+pBdAk!s0pD90DUV}@|6abF<Yda+uveI(~+AkSarBZgZwpLp);&;4yU2P#M5+$ta5oO{(*N9qkJ7pVrkF6zD(Ge?2Cs3+ybZ5{4!#Oqp*+XmdH>>LF4m;>Lx_NRQiajV8^$YZEJRqshs)1{_J^^_VU)k|uk)C8&FQi<F@f%``>S2e9_y@OO|e!dG|2QhEPc5S6*3heK<*`FGB2K!h0N$q#FSJnRP!M;>10|fT7+TX)Cj&Xb)$9?12=i7WehJ6iSAH&(cqrh39_I&`y)q$^rxW5O-(1~N{!MugQK5fhP?WFv8-s-&QEpQf$=lqT5c_nh*UiWwAymjR`%<QKL`#1Agetcb*`|1mvP3m5q0jeHcnX8(q&iCG&^JY9wcOI(^->bfX9E*x6hT~N6j^=hKKQoYRR6fEuCrW`F`v}hS>$7(fugP1?)O|mGUfD(Uv$Hoj{7?Ty=HDM(eL4K;Kg|5+lYf3q|KpQ|($~LU+N1h8s=UYp)SimXOPyBYpDm9Hy#'

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
