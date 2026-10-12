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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/fcc3241662174fbbb146e6cf658293a9/part_002.stl', 'relative_path': 'fcc3241662174fbbb146e6cf658293a9/part_002.stl', 'source_sha256': '980c7a134e71238d37801eb38e53dc3af00eabfa8fc9523b62c0b473e93e6fbb', 'input_faces': 560, 'input_vertices': 336, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.35530054569244385, 0.010205822065472603, 0.43671005964279175], [0.3617055416107178, 0.06489116698503494, 0.46877920627593994]]}
GEOMETRY_BASE85 = 'c$}r12Y3}l0>?KrrGy#?E$}Fs&}$&H<PnM#fhZ!<G#mtJ0tQ4tJsw9<=}o{0_(I1Jq{s;Z`j8@^C^nFj=;H*W94IGvrw7Nq+4;@h&ScN;zPtFnZ+`#Z%+Aj4&QA7iFs*yRLNS*7sbMYXmDSwxMKJOyVZ~SzGcqTP7?Lr*;h1rgqpZ@lw|^*?^z73ktzVQi(Rwa^XvX*<nenZC@ok4C#n<=64;z~~A#?DUC&p$D%@Drx;L+nVB7Xev!Q(O_IiXpz7WIA2>eTnW;QJqcibaMHNZx-cB~qpj|J@c*`it$%OL6<lC$`!?E5p+VrdZ#&y>HjbZSH>j>%O*qc;e12US9QM?HlXqLy!Hed8^?Bt$*wGw{pLYYHhT)+n=X-zw$j#o%Qm8=+(0QuCVO`<$l=kTi)p(A5>oTj}LY0yYaWY*}v0X^`G^fJl?;*qmRe%W_zFVYQOmOVRJTm^`pGmPe6I2AOE7s@;Wa5<!gJ~B`(N*u2=Q+s(rBaEl(f5d`I(E^HW+s{;3z`cy`y+`Z2xgNBPi*lb-FBSM38y-)rLumHf%m2L|4?y_IuG_A_p=eq9XjoKJjMd38SV!D~A={+2iUciJ2MTd~cx@tfWpf8fhQp6!))+7G=f`+4Kj9QSomK9Cxpt6lfFD{?+0=jCYE-SEzJ$LE_ThBw>$wpPjYYOlO%Z=GhpIVoEIrZ?N0^IUnW{T|PLly~Og!mDyTPu|RNpJ&sn^Q?SeW}#fK_R6dFfv$g%{+UkNIF)zSTXkLbUXy-7as50S-Z{_s(7<b+?Ui@V+cVeYan+91&l^7d=sEqqZuo;dZ(W|#?jzHyd9J)qdF~hG{S`jk_*>rW-)V33pFV$8j^{WZAE3>1>k{LcRdlmmc3Yq4_UXqTv3+{M4W2$U{eb3u+vZE3z1h>JU)ZntVAOuw2Y$)*^r3lsG;b|CYWv{9oth8T+$`s(n$L!}uH4c6v0mDJXL@J;Xa6XD`6K%LH@q|dl`qjC*Rws|ng9K7NdMU-ZJjZ_v(77DsdTPqd%V-W++VfpYh|p-^YjxpYCbfogS;-6HhKEc>UVYjc)GkUr`LM>HxFt)@Zz&_KE&jB`f%nx-FM8A;~f2_r}tOct@-d*>$Q2JytOvR^LUl_mkH_p-#jDl3xBS+f8ZUxpWatJ_p8=PXMI!supT=1>5f}+{4YGCuMdWI)&aA<S_kmKH%@Kz@*(Ao{*`z7AN8{~PeM7_o?gup)2DxZSo6W`cG~)2dbK_%A5Iu1eYLfoK0N%8=B=Mb$@70A$J_7OtB;d)NzE(Mt9hlons4g*I_;m@F3-d9kmmjP;Jyu-5506j9+#z$CyWoz+M=JI?YBMm8*VgLU+2|+4=vZ$L({AE(DBpWk?V|FuMF?3Z+P|mWA?AS*}q!H%yFvq%Jk-Qk?EcFS&eg4vcBFL-W<O_VX$Za%A5U%_KnuZS@c)W`&xPPzP1kj>bVZ*^Q=pz_tiYCd2@X>y;`3gZ>-PxJnOUa=K5@UwLUxESf5R=?jz;R^;vmyeKx&XpPl}V^*NtseRldW)@SEDFh8B=2g5th56T<Ae@*YqpXdLfJtsK#m*JiHsl568V0h>GA@R27^QY<6`menC{HeV8{Aqf#fAjg%>EC#sG`-dCea)NCnWk6InNB~(bEfIl?-AwA=S<V9=S=6k8PA!a>$g3htCcsOKTWUZkK>K!Pt!Z!U-0>!+c({j$7_C1!JFSxtik`3_Z{DloOy0|XP)ED?@gw6=J`D9v^^fyLuZ~F-kIlk^LwA;&F_zfcjkZRDBG*=zv{S5uZ~OkeD8nm(%$&JW_ss3-qrgF8twCa-^b_szHfM^{q6#`H{Z{gUfp-fo9}0oH{Z{g-t6CeKcl?){zQ56{fU)XP`2m2jhYXpcdq04Li%}A@2?E+wC`I)?w9vw&UH7ubKUXz-kX)aNA_>L_j9~@pQidZywgA4eD4=JCVgP%yexTtPR(=s;FVj_&t9(i(Ab>S_I9^dXg)Bdakf2Q#%5{We`U-XyT8lV&uTvArtQ-^PuJR8?TW9p+n;+)?|)`+o!x)(z4~}6ZLxj&8K35TTi>>Qa6&7+pVWi0pJNYeK78t9+0W2XdOz7;$bRnX<4jKs+diDNQXjwZe%SQkH9vTI^SG1`F0SF}!wp({@AnVAz59t9?dkoQGd;a?-<kcZ`%aw)<Gr`(&Gz};dr!Yt_Frz6Js(0d?#Xle;MKFX_vMV#ytz*L+ZL7c;g{~q?d?u3%X53*jiu|{=Ra^u`e2(?vVWhPKgwGN58FOmig~iNm^`jp!<T5+SNZ+X_WTchK22*MnlosPXZxXVt<mNu-u(NB>7Db5H~&83?AQ4Fi0RG#&A*TMhZmRUd2oMuzgL#W6{t}{o=@ZNLCTwd4>G;;zI|!5^v5sGaJTpOC@IhXw+9y3=YQSOJh%59Ib@%If8*;~d;jzI$@S{UlX5&oO3Cw+Qh0?n9(-uv%j-1%p7epj2bS6WupT=8-8-x7{Y)J$&)cNZ@;ZLkC8(WeeBk(xwhtzako`0*BYp2)^W}J7(0qD$wwzb7%QPQu-(U8l*3YZ-Q$KZ<`#dNg9QkxmyN}kFmFK7AvU%ElhYu}ET59+AVG*spZ&9-q?*5ez44NNw-!J~y7<s*J{503j{2f#IK;`Z7{OnEAeDL(=^0*#-NFMJ=+7FxcqTOG=!n&`1&^~Y0v)9hLeQ?|MS8ad3m)73ewnbjARcZ2iy<A?Nhxse!*yZjXnh(A{V}*7eI#iJRJ$CLTJGY6`eZ6+G?Hre=`QZBY%iQx&`Ovw6E46uY8{haxd!GBtvfr^4Wj}pyE_TmD<wG~#wy#%sSar>(r=DBk<pYzu%JWkoN%z?UR=K@Dp^}_$tEaAXU-!T{>C?CW@fGbn;{!AHtaP6@<$X(vt#Xei5M5Qaf2idv+J0MA<M-_Rg?4>zHQj$QXtDdgvli8qe#hQL?(tZS?w9@7xzF~YE-mv?(zJg)&?jl?+)(96Rpe9Dim`?bcKy=<A;pg>z5nUJi01#*KOIPH(fI%UrvvXs#;_*x*+;qB#Z$?md=8!&`8<Ua<uLdm_$jy-c{uzKJd`{Q9uB`iUI$NugX9pr4t|%s84kf~$TQ*1@Ko|x@{90OWWl}3y&13Ik#KK#IC(le5}rmDyn(!d@d|z)-T;TlIq>`NW^xW=+)OzW9!Gu|9!q`%9tZa(kAfe8N0Mj2qu}Y}jqnV316lAv@<GNccnf?G&LMAMj5(Aq!ehuU!Q;pe!(-q_$Rpr~;Zfv2z$4%pWWnpn>lwG=1LOmYSMVF~0eB1f4aT^I@@055c@{i|oCc4EA0|Hur@<r0f&=6L;}*OY4#4Zl@4;)~17yLQ$eS3q;#uTbj8Sj~`S<W>a!)t|P9qP2d%{nWpNEIQ0rKnc^YB{oe)x6xJ#sd@AKpa%J)8~CA`d1{hBL@L;K6WD^6%gt@DQ@#DdZ`PSMVx$3j8{GFT4ugPZqqAypr+mXMEYX$&69ta#5CbU*uDZvMF2(ZbI4C#Sf50*%cPs`l<I*C%8uB(>U^JNSOpTgj-U!cX2IpE%w=-ZOc(#j=Ci3#r```c7!{?-6=b{xEooNo#D0|OGnCXa7*^zj`Bgc9h^+r%f%hY9oT0twrxUv6Y3tMUhKaMWh=M~oI+XK#jVMrOn^IaEUhS8!^!Nw4P{Tb4cwfvhl{(AyRgq5Y}=js?$oL6MSVTWRJa~old`^x<H@2d1@~ZIsg&_>Z8!zKVaXg1m!kZui{qkX7UfUW)#hA@dQrx?xGq_gF>o9#wio41>)-sdC9^3128(T@*(RDcif_|aly~5t;lEM-)5S%iWESN;u-LY6l&lwJ5m;R7M6S0eTfnX11j@QDE=w-U`0BE41?nqMr}$S(W>NkF79YXUl($`6h+`IIVOVTika|%Tg2lboC`#UMqHG3tgF90uy0{Fv4C6~=+Y;25pic4MEty663oJf@D^ULG;sPA2C=0@3+bHTqSpXJmU7aYo-ifjS`~cjQvXP5#Su%^V1a)HD^3<27PVxO@QI>|qr!>b`nqyOJkwqB=i*4_+&0XpQcNKM!PdCbV_&!V4b%F0E$I#|}xI9_3serFQo#0ZmiGfR#OX4cPrO3r-QwqM9TohLlE=Dd+n__SYvS<^HkETv=8QK(w%aY6CqTw>+nzShc*CN-(m4j=#+H|6wC_BRsP*)r7<Z3&CcA|U+7H!5;Kb|_(b{FkL`A7I|>c+#n$luUr7yK<bjC&jY#??lwIp0#=3yU^)slQ8|Y8y*CQC5U2v37~Jm8cWhN1Ir<8o4^I66_;ap^Xo&O0JBn4p(utDM~w07K4jZR~atqYWrtPwiD%duxNA6lJ%neGrWg3A`5<pyc>58-s5UBiFTr#2zP}i!QIHuTJoNoMA;R7mcDkwlgNc4pCXq05oH0maO6`^Tpu{fl?%}J9$W$16rx=r`iP=U5$cOjC-`dQQ!>)v2lyKKdrP{@mgKACQ@F3;@5!IxPQ$0jU*i4*e@4EDy99qpzJj|BUnF0{iLqUyPUJJxU4_q+KgE3ypCO;Xoq|6lAIE(LpCEsP`w~7*K8d>se?<NYcLhF4K99Qwe?>k*J_8>j@4$TuA0cnWoq%_cvv9}Zt>j$XM{pK-JMJW$OFoSI3f@jWggXx(CeI}wfoGHF<95Jv$zog!@e8RFyokCicp-TKE*D-zo`>5GFCfps9fs$TXX6gRbI6a9=fd5|VqE?4{izfDICTr*{^X}|i{Qt}gK!Jrr^)?r^WZ_`KDaq>Kk{tGHixng+=%=rT%X(;*B@>~7US~c{nQEWK;6@@pPYgl1a}~}!u5kw$PICQ;8x`NxbAR6avZr4T#;M{*BXu^C*u5Y9dbKd2RM=39G3#OBPZZm!Oh84aSh=Faz$KyxGK3aIS!5`*TB_*E0dex65$%;7PxkB6LMo*bGQZBhf9DPlPlq>!ai~=t|DBCT%BAQu0pPds{vOhC*hjF^~lM%7H|@|C9W}?Os<Rb!7a(vaFyV?<SMvWxEi?`xjNi{+!j|4ZbnYUCBbdU9dXHUD!DzbCEStR23HquPi~5<2Dc$Mz*T{pk{=^CgC8Uh#I=PVBd6n1;eq5#Tt_&a`~<E&oJkhr8h{@_o#4LIHH8O|AH+3)`;x`DR^UYWD!h!kf$$3QQd~N`jJz0^2`?ot!94*lCclCk052hnaV^I$r)~h_>dV+(rB39d<Q4ES@>{rN@KN$M+*0^0@@u%o@HX<BxFzswWHGLt_?^@V{(!pW@J{kE+^g^h<UI0G_yYM0+*@!S`4ikW_zUufxYyuM$RFe0gg+#Ij@t=;Og@YI0REhO0e1{OOa2Qv5B`yy);+2~Ou_&3zs~;qCm<efwf~XU+*1FunS0CRNMFt$(bBpXwx7QXME<jX!HHRK{R=;IE58'

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
