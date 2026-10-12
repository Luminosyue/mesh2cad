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

PART_NAME = 'part_002'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fd5b1428b91c47f1a74d98bb92c9fbe1/part_002.stl', 'relative_path': 'fd5b1428b91c47f1a74d98bb92c9fbe1/part_002.stl', 'source_sha256': '3f622846284d6bed23f2cb874272a75e06869c55afa0752d4c5db9d3db114897', 'input_faces': 270, 'input_vertices': 241, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4957084655761719, -0.5, -0.22933977842330933], [0.4956889748573303, -0.4806324541568756, 0.25399506092071533]]}
GEOMETRY_BASE85 = 'c$}r03se==8pj78p(gkUwRe+`&{TYNm3%SgD<zdIDJ64`2x=G-;Iqh4)J#oG(=08=EFVZ3Dk_3Hyyftc5aApSc<g4GkG$2rwp#bLyv#oTJ?`)5UF)uUXRTTPAAdIA{`NO}X7=nwSZLE`0g~r<Qrh*v)KL$1k|gtNEd@vmqv8|iMn)wB#l|i1k=iofJh*P2IAucER3B-f^mgE^sD#M)z`=6h(CFa6UUFdc{P@IpTkMSa@w1{#e~fKjLR6!lFvk`b)%bJw{?GL5B@gJ)OHPvi$D@^*!#9~1&oqj0`!-W);qII>g0K1hN__qJ0n*+*J~vPFd3(z*OD65L*#)OXpSS0}dVUdY-@URx^sV;rjh3Bgo{pOa>))>p9oMM1BGI?n!&lngPkcG+RxbN}x62KpulR30#eUz@NqlL~jeO?!scI1WHGcf$nCSEN+}Fd`dD@51^u%%AVEJniD~PWe*FE{nTuAdNU0le<wO}%hGh#5yQ(H8N#yM8O@>Je_p61zcbFt`KdBRth52NFqX3t>l*Y;+<elXXgw=!A&a!Oa?D;JNl{MCK8>P25mXvk*qQhy`9TC+LdGY_xSi}`C6@oc<GZV~g{{Q7=%e6Q$Rd2+w_B=MEB<g@JO@^lhknSGdzOLcCqC-sTXwu`=1ANcyE4J3c*xBi8mzkkIO2fnc}n#Gs>6q?U{Em)qC|8Sa5*;r4WT{_YBZFjQkq7A#^B6UzhHi^Df2l(pnA6#Od#;;9Te05Thi_D*=cJ5>C!U~u#^*-pSzcSV{AEq5~k^9S0RU-O#?njR=zxko3Umm~P5*9~(H{K=IN18E+^(!rZ^WOPyA4c-mUg*c-=sSkc_DQMix)?>*>sWnyA^$@YJ=d}Lr#dpPmNsl=>L{%f$EB^FTPph2^9R1WA-9gyKOt#-h~QiKz?Uwat|N8$JeK7n-P%@1>R_M9@^J^)NE{<5nAOvG=v5lucjx;o{_u`;yfdAiI!t#t$@TT?yfQ@ac|O_%iN%*}7o24NPd`#B`c^*h<uxfzlK-(B7GL>j3G>aASYB5a?h$>Rzc1iRTNXR%xHOiJmfhDWj!POUd-5!hNgU;f?^k9V?eb-ZI4&h{3~R6W?stfFaIe*NvpNLX9OOQQulAqjAoDzCI~y<etvtCO(U$mHz#LEhGg>&rI_Q(L4u=Rn&!78}R#q#HR~grW#nD&g)snhhK9tV#ESykF=5y59Z%kjl+PYR8ml}J5`AX<(HDW%-w40ft&*O7nn-xTS_0f$dSo~ea1+ib_>ov!jpR@V`nGa{?FkcE?UrpviiOmpwYh3Wv@I}Pe-)nn@<+Gt(H5qTvrBlpLZ8%T*9hc60<)ySL=JRnK56@-&hVQKs^HF<G&J%s!p8LwG7n$$o_fh*JIqZJl@l=)Auikl!#~=B7r5Hzw%*ki*r_@%8{VK(^1)|T}b6-!|P$~ASW%OimjEyms<oXu-GT)sRTuJ6(@b8}IShJW4QiuBFA{KxAwQ`bAzf)&L-^vHRJhif%<TEzEkhNd%SvkpP`VQvH9S)R;_mSokQO5e~xW9zt316Arp+xLg-*cjv)h8>-F7~Uo{|C#*D4lL6_3v54eD}F2b~4Ye`jv>jRR`{0OD+_BIc*v9wLUEh$#sADgq@9d;J*sQezk!snXfKcQ6Tm!eSfu7^sV^-U$M2$CG)M}@6314mY6T&{p;>KgZa{?qd8=}Z~esbl((kkkUU?0!qe{q#Ri$@esSfZZ}kgbYd<<$^tFiZ%0!>%qZ}H~d};n?Sz^EPIe+HM$Hr%pIwZ$bh`v<^?w?(gLE=ZA_r$N6mvOH=<*~btiv1eze!<$Shy4$W{p$VytPp)`UUB~y#{sclquVGJ-#uXF0Wwd@FEL+9Ihji4;Yfc^`^duGWWFsLa!&NEIPlf5xbII3?X|=a#J9$K`gZxfeDC%=fA#)E(w^t(4pf-0SLd<!n|Gev_s&!HIguK2ukr4jeSow_edL)n%)hIiZ}=S+`{niLzV~%eB>kw^FTcLh#+VGTJ)aM{_FjhAFP}ep?6^#^Uq0Ws?>!H-z#Um)zkEKs?IW|r_WZuk&yLL|{o=mRW9^36uazf!@BGzYzRnT*<@c}qdIs~o?{_8tc8=IDe?Dm0ez_z*o+tYG<N{I$Jb$?F{ai9O{j)&qmp|X!>wF7Io_HP_V^$T4arpC7?LEa#<{O^3+`sEN+<m&8j2F*ywNsLv%tJi?-RC|p7u)mqj+$|<Tx`$ZQ_|k6<zhbky~h2!-ghA}l_WlY&-UC<N#gVOauY`-iI4X<_wRbYj}NRO<Hh<x8Zfzv)EVmyrP<ypGOzgh1itsW#r<l-c`-g;7a2p_RWtQkN6CMzs}|$)^%(cP*J<+n)fY&7toMwGITytEe0`|@5m7_t1J;?`_g;Uh+gjI>`ePldCr+p(`D5Md_G{q~<MVYj_r2HKs>|jO<6G<hjC~F<KL1{jo?Gf9_2J(y@V&ol)PX5ZQXhOD$*o;ZF+Tq;Q@-3*N800iP+y<NeDCi~?t6c4%8Rbnk^1oO++Oi65+C2)@}EU6k`ML)q-$4Pq+fiGbKm<rT{`$mJ*g-5J@j|d>&5tdzeS5HsweTWZ^M1>{Tw~~7W2LLk=#SOHHbdncanmGh;Qvvb)DQm#*2M3qvZ<b^L-DsWPiTsd+*B`&DPO4*vC_Erjt05>m+Nh)PL(~@3l|JeeZoj)!`sM-)~e;x4J0$*1qM6#TUi+e7}_Y-utN1JIS;?_G7t!*FJ4j8fnk>d%5qu53IbNN!s)MWbTuF<}k9W{>U=Lr@NmdnP*EWK#H~rTk5819$fFer9StW|87ftP~ZP|OZ{MD4*Sh%iqm8r`UO}AZ-;&c-VWXh-3HzY-UR&+Z0dUOCU6S$J#Y$mEp$0}EqE35ZSX3v23-i&z)PWTftP|8K;Hl_0MCQY0?z|SLuY`a!8Yh?U>i6B`U*G#91fif4hM%pp9hD5M?;5!M}wb*_5(i)?g8xv?g4%r+6nwPxDB*5xDB{Dv<0|1*avz)*azGc>IZHL_Jy_w`+{3Rp8&T4cZ3FlJAyky2Y@?+gP=pfLEu5qG2lVq=Nium(23A7;ECWDp<}@>g2&-BS%D4*E8xM<XTXEOeW1O-ralGk1MZL0<foyJf}aL=fd+uPfFFUj13v<O2-+6>5comp1K<b24?|_}!{Dyap5U(FzR<sb`+|o+L%>78BcbELBf+82m%yRmm!YqMUj|QwP6tl~zYd)VejOYMoehoz&w;)Po&%1B#)D(Q3D8C01n^?$yWqv(B%CHEL*D_Lx&oXGUISeXUIYFBx(@sS_#^0Mu&JMbKLURY{T%!;cn5Shcn5eFbRXE%J>Xs7y*N!ygMJN81E)g|gVVuBphv++z{jB{z{kN^&}?uP_zctlp8@AV^TB!GBIsFg5x4|e3N8UxK+l0Iz?IPR;7V{c^a8jV?0`DK4sbox4Xy`Yg#HzL5!`^&<nN&0gTDh`f?fe%0{;m88T=#oYUBA6^ak{2@D1=y=-<FM!PlVI!Pmf-p+A5xgX^F!a2>b?S_`fLe+#Vwe+w>ymV?W{#ZWuA7+e4?1Q&pFpt;~2@G0nN@F{R6^dvYFoB=%s&Hx{Regi%PPK6!-r-HwPeg*y#yc4Q}cY;5KZU=t~-U8hU-U8kT-2^r@1-ucw0lF5v0sKC675IJdN~i{230?+W3SI_Y0$l)J0#1a^11ExGpwZwMa1_)AjsmOD2(SvC1`P*K15bg5fv12cK}Ulpfk#1~1&;y;LwkUO!QG*cgS&$tgSG)b2KI+G2m6DYL4Cl@z!J2nbmuU+3Dg(d1biQ~75F}IOK3-MOK=BhXK)Ablh7dWli=RaLEzrtfzao`1HmJtJ8QBLI8A<`@r-Lc=Qo~n&1(_r(<GqjfBM&@JBP-KBK{+j_g~V_Gx0CO8)I1?Yhj_y&Dt~;t_k~4$TU|x(!T+z&Dlu'

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
