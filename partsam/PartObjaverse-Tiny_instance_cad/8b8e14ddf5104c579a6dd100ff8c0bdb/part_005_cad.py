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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_005.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_005.stl', 'source_sha256': '17fd6d9acf3e16b59936e70ead80258964d55172915bcb8c4454e13e136ed62f', 'input_faces': 468, 'input_vertices': 271, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.17833448946475983, 0.1579292118549347, 0.10967399179935455], [-0.05004939064383507, 0.44244423508644104, 0.19566744565963745]]}
GEOMETRY_BASE85 = 'c$}r12T)X5l!hMyDi~%|#5mfDiZZSd6Q(wdVN946MH>Yp3dS+b&}K1>IV){e%xM%Iv{ek4MKNJ$GX~6J8g)76|E-a&-Kwo!rcV7IznAmQJ@>x*UPFz46K59>17AgqvM+}<OwMN*5?KuoV`#|0!M(eO3@Xz<e7KYGqx$moO=mZ6+swbClQGm7=^Y$0sQW-~Ka+Qj9#y?do4k934IDf$sDIb6fx#i-HwX$H6q4o->J=0olJ<Sc3RTLNHdQQD+Vs2W|M=yeR)Q(|!qEe1YMcGwV(m0FKlyM_)R>T<zU9vs>KpI8;a8f1@$Wyu513{bwFgX6-;w&_f_!i4eMo)dR0PI1J+HpiH%jxE@(soKe~e3d-Q*_lFZNa6wD5}Nx4L^C*8B~+qMolG6V;!e>yY|kZIEZWljbpaUF+PI$YaZid37lXKkrY-^Jq8f34W@1%u{|up40A{-~6W==5;gmi2D1U!Y`Lg>#?<btiH*fUGq4W)W!HVci;~$j{Y=ibwJhkD)Q{Wd<~x#I^NtVL4Dh<lBj2ATZ|ulR((s=HwpTE2>NgBass}yaan(U`VjRk>y9J;Zddh<HmT@;<UWjdKZiba7#yd0eqE076Z@W1|Nf2r+W);vQ2)JGTBqY$5$%uBawhy-xzPuoI$EdsL8SU-xA-&KmobMlkG<`9_+i)2U_9n)KRgce-PB93Yk0R;-<EAG{HPf1gUzqI)@klM1b+Tn>YJlRpiYlLm{*do&dcOFU43&<Z`7GT6!V%hF;?e0sT=ZqO4NSZy?)nuSqitu_%oH&H!psMd0lRU{xt1yUh6dcu`Weg!=L|A`(sUsMEylusBiD`;FRXCG70-Fv>C=%YM}Y8J657UP7Tl>p9J)0RadRk7*rGE?>5!z+C3xCx8^l4zN^bw{r=TdU3a@rb<E3_h;=C&p?$M0@PnUZ(LAO%&gk1cU)1?@uGVShyuSI4lxw&jA9&!tbE|+nQ%Y$4whu?O9!HKssHdLKX`R;}OL0ED^uW4|Zh`$==Csbs@isH^yz8OsVqZP);P<|x{cG&!;p;K4+L^E}=lbb*+v#P0YrYT{T(@l_t>1byzs}1@{2Hh8y0-F!`VSXk|JQ?WIrLHU+f#8L*|&aC-@McLq+WMZDfP|&yvO)q?XX_IAHceJKgRfm%{9M~w<y-P<OBHc`ykKztGFKzTvOi^8lwHTCI6^-%)ebx-!|^1)?+<e6X%$FBI+-BN%w=J=xCj<slplL$$Sj`%((D~=6iAsc~<?c``<p{i2CM;IE;T>1N(N*VazM#Fvge2f&D+!U9W5Mj6wZpz8u&5YiFT9!5dJ|_PX)<{iDyA*Tpr+zvmeCL&JL5Z@r_~&z!n0He(9<Hgf^`S^25X*OYJ?eKY2uo`J#0Gq5=B)9bTv-B;ChU)jx1(4SkAk$=yhT8|}W2z>uB7=L=W_TT==k<K@t`KtXi;(pNmY#bU6zht7$*U_=w!S8+Bw!OOl?FYujrStp6YW<cLCe35++yi;+<+0ydKgGF`&=UQb8jkz!&vCkrmTirY=TbDDU#_WGuSPXdf9F`8m$l|=)W5qb#)mkrV14i4{J&8N*X=v<nC4&93(qfaU-+T-aGos4rPsB)ltun}gK;kTeZqa@QyTf7jl%uql1F{>ol;n@SuNGKZfc0WMHNurv2362LnBMQquRf$@GUdW={j1bchGrRZF%53#cTcM#le_YjvtUG^^W>hul_nOTS_+6UtzP(%j_PD@qRAoXHOfRr>R5rx<<Fphc*Ah_qe|nozprk@7}6!&vXj=*(*2tcIm15wpvAWyxDmy)^Yn2_04NNbRF#*j_NwvZ=ZwzdbZYM|6D@rv9^gr{?|`YX9eu5Z@wj97M{NkM`8bD-><%-(hBq;gAc~9*{r^)Xaf3hD<k%yXEd&R&<W>iJ}1p%U%v)^5sU6~W7%=dV|r^tey`KGk6Jy|{@W)l#rW<~x*x11D{CIh`vvf8;C?sOR>O6t&V?U$3itb!nVR2`I2-di9D(P{fGyg8bBQtNXN9SFUKGj&fBtazl~T0NR{M3mt|Q|R_|G<A|IFX0<1MYi(9h!DT8}9p2>of>6W2Xn0{d`vAH265?twZ-Y}Ni7;~wKV^0+JV5163)#M1dL@{je0-|XB~?a!>jx{i)lP2kUT!#R0<0s0(LoAZj%@pjLpxWBel!*y3x)4bLm$=DBlD#9P!MtysDDcmmuytofN(dQ`@@xHO3AoBMQ({(ojd+Bve`}1MGbB^MDFSHx>dE4w5A9xS_^c|z?YssD&{(@6lr@8bFoZB5UU_aEEt-j@LWAroS%OS0EY;)9;ZyoNJaj(@knLFWJ+FDfmYI*ev<DCPw4qLzmJTIbOsBaIPiu>QM4fbJP_~z7WcrM?Wg#F*`8OFC5s{7C$5Rdn|$cOM9jj^9+{DS^pyp4J$EW>+svrJg$D_7Nb)bPZ6-Ny{r=btaZ-_c3;p(*Gx*5_&>>ZySJY@Er6J|~?=ewWX956M(R^BB#KsBg&@hI1xYExoSw$VT;TJA3JUZF^k=`76SA+&qN$Mq>~5f5-LkE!Xk>_Dfdy$JQawqdiw~pI5@?ol5ZS)hA-yv`Kj1j#vY~)DHN!M&rCH5&{2V2=14e$?&fa#(WDL$9z_G#XfA&3*#HvQFodB$RFDieaO)s`^2*w`ctMW`Y_}T?z>3`HJ{^tXUuD_pY9WTui@GshpiRz7dngme{MD28>=*gKe9WXza4yzeD9ksWX1dc`T^;DThKM!kA*|A??(TEda{?pIrCdvtV>{h%=e_1{=BJHQ_S~tZTMH>bsstw-NJsWRRw+-^U3e;ck_qR@Q;?o^Vlsv>c8ZTdg?8^rsE4f#{K?JF^nH|A|81=p>Hvs=+C)m9dF$`0Da!?j`_A8roQd#WaPh_3H@=ah4qR|LH-f{9Mt@QkFf6L;&J~be^TG^+cT`o#6tM@D$mrnt@st^N%&{vd;SD@Ms~w<aD)lx=cxzk+i&>eJ#z2}^sUAn^-U|QVV_66#Q76_8+m4b!2OxMC(e!TNywAb2K%GYWt@|}&Z=)I?20<8pF};|Pow_2HtmCD<QF`bf8CG#el79d5)grP2;YZ!C1%ofw;W!F=k4AYjQ<pb>+(5eZ}u1J*}DhlPjVStx8-K|TY6%j^~U?5)xI8io|HfN{XVgcjDkP<G0wN%&oSSMOHqHZ%38n4VnIK~PC@=-ad>Xtn1eo_jzpe>Q1m(fD)hNTF#P3RbzSUUb&=;r5c0c@!T$L;4Ci_Cj>x}uB<k<B2K&LkEyl+<;d7HyAKVum>L7ng3f8aj1Dp?k)Pf&l#ym#{AW!tq@H19H-52U(`~)BP9V78R_hmZH`42y(8*jc+75(4!1N;T_Z<I!!flk<0;~U}JTlfm|IFV#mf82T8*SBKvo|Pv-eOpo<-OrAPuW_zqUW)NAoV7pp5tFb_Do$75(!6StexG|Q-dlVp!>`i;erE&zg+9n%u%r6+iF0&6*meeDe3Sc{-|_QA%;TXS{K6;kc`Ydv&!ecS$W!bW<iA)R`zrU*16t=KoC9ea9(4xqfxq0O<Bb8ac<;(Q4Zg=zyf+Toi*+mz$nhDjVm{c9#;zCpb=|9M!uv_`JoKlsyZV;!a(Z2Jzb^2L-j3DrZ>DKKZC+tGx0?=E-?H>9_S^0?xSwtnRNs{29O~rnyDTm8s&6wz!(X*0o$pwD2mM^f_oYKw;D77$uElu&JmQS}Z!6%ua@~jfdgz|N)eqox*VRX!ttHjBZQH26b?p<}7cSfPq0fuahl&l+x2hH3ziW#AkH3O*vTMR#t>-`v9d8}A0{iWKi2Am|@6m_e+3=j~6$F3rE`0u)avAGhync-4Z@Likx_=etf2)gow4WtkqRu-BxW7z`)Hgl-`MQqd`@h*|jQTdGmg-v%?!|n)sv*x(JD$sP59oDm_X@#(8G!TW+jFpePUKnJ4DW%~*QoRTv)y{#iq5$2T4u+2(;^)Hl+V~FS(e~ATiEL_&EuGj{Tx36`(g6nUD~(s!pO5U2=9+B9pDe^fqu5@g#7tU@a>0DPxtETn`<54sn?Behx%VXK%K*9s&Cous(mnjY>M~Bq}J-&Ru0j692*N@U6xdXzv~&+>q&jQuTEdPL-P-*i+)B%q5q!Swrf2%3-Nt^8R{$%slM&^0Mvi&3hG=^0Dk{v*oU{@;QTx6fjl<6zuC*~L!MSWx2gZU3-+6DJG_@&FA9HMcJ%Y72&`A~`mO4ph=*?p!}%~IP<_kSGx(gib_ME5P2Qs87kZ%1<yr8YsoYq7%c@|kqfdW~A735gqlzK_z#!c3)hBM&@vVC!PvN^d-j+B2Chgn08n|xJG5Ed6-G>|158-`Oqb}xEe7X9T4mihb#d6|4a;^=(RbS+vHvs!&kRSZJUGO=#-zfC0=9Udw=fyEN2eM#aIV$&nUl70dFjhB%pVPKp^W1iW-!y+Z-_gAs?$ZHz();#~m{)9$^m(FZ!f%r?y}tzgu>{{d_PuYq>xK8X`<v4HOD<p^hT%Q^n{O*#5BqlAzPQ@{>HbPI!^7omxM$j%T3Wan9!8I#@BTz2rhI+V|Nc)zy?y^ze<Jd&T=oC^C!zvrH55*Zx(wk!YHhM;Epi~aD?_*)wJcfGo7|4vm?7MN`X6M`s^kXbMhszpYD2PUH?luDoH~XaPM*mSj;78gN0T=)gqKpske8B&F@!r&yOF!GrcMmuIt<}T)T-pFoO30Huopu(AJv=e&7S6C2<K-Am!Q@n*W#L$U<j9H2<M;{CX2e0bC6va!Ui=XSv0Hh@0V~U>d)j%WKV{$AGIl2G??s1?wA%ssee#|$)Y33qI1cAkats$kwwptcau*tgs)N)$ydpaw0NEtuhQZn^)dM||NS9D_$EX60yUAG$ZK4n9wT2MCoqKLsB_74InOwT@H&R@RBCs!XcO{OazBP}3u;NSs0X<Pxh6xn2DJcLv@W>@xdTJEKQ)jn+Lhd&JcJ=UfZC2M+L%0m+?yfXgW7;B+KAkP+>`20?n&;;5RRaRlSOBeBghM=(c}f>?bMCr?c@UtVH<TRS#%iLM*fW<+=|+XELw-$ifm>GSEN=Vi+YhOl6@G$d8zrxqWQ^r$+;QAMW`jnqNT}2$R>txHfj#Cs0%q8*_mpPoykrN`EsRZB8z&GUCBAAe&n3watz^?)Q;qDXG%+k@L-1UN`~-q>L29g<W<z&<W=P3)RW}n<jd5n<h#^6)T?As2l)>93H34g3Hc@U75OFk1NAxi1NnVge5JmlJ}18;KVt|#pgtsv-XuRD-=JO~izbk7kk3=&$fE1W=gCJI!W*bl$)f$p8_1Iw!lBd_WYL=BP;zI6aC>SEvS<f#dvY&^@F;43vgi=<DDq^6@I>kWvS@GeMDjRl5ArzjScdR;YEQCgU-EczBsGE@NuI?JUPE0#UPF$dZYPT#AjgpH4B^#O8(H)>@@n#EhHwzI6<O3w4kG``5UxV4NEY=WS0Ptm2p6a3C5z@J7bh2D2$!N3A&Z*GrO3so*~rDnKQe^fsLo_jC$bwk1J#wBft;BkoQs;1ELx77i|oq~4xqLqiw-6Skbh?gZ=tRvpQfImt|Xrz$5WS+MOTqUkCR0&ljF&k7{d3Af6usk4B;2lJ7m!(WYL%87vxmx2XZR;3-vwu3;DD0?-}=*A?)OY5O#J#2xoLc2)jBVgk78v!v8RY-%{U^MW2!1l2fP;$SLGxhVU)w4e~AWMe2F7=uz@T@+pRJEOi4}bP_q1yo4carG}D4JCm*CK@8zAYJ0M1FLD@pBtv*Qbre~2GI=_A9(5vl9(fT%cp-HhS#&IUA$b{fJb4*8iXps$8c7zNMP5N(PhCS^PyUM<L;j2WH$(Uk)lL>&O+G~4#1NiA9ZjA=9!L!$i~dR;NbbTAZbq#_7Og;TMy|&Yu1+mZ7A-`sPA*R^MJ`XS#t^PdEk+jokzAQvkm^P*NY2g>&O*&V7R^k~LjHjvT$GxNEb2=xO0Lfk4xt8+MSmxUkpE-|@1t%Ze>*GpF@(=Dgs(G%lc*=iN#rZkc(Ujv@)h!Z>OJy(@@wh~@@w)(YARXu3;82CgA?>KSyawG;q26G4B@O)CvsMD7OFEj3)!8Tk?c-(qq>q^d4{?%gfpi_CaOVo`S!w3{$xPq%>Bd=enWjrenWmrO(BaWlb@0wQE!nSk#94EuTd|OMNg5hk<T%Nk5FUDqD#m}$lDmg^Ql&{=pgcZ@)U;f1Zo&rbR>BKc^Y*(c^Y{!LwGH99$9n|c`bP}bs>2(c`HMB2Xz@)G>W`~yo<Vmyo<btA-tEmp1ha5pZXVB^l$Qh@<Hk$@<H-phVV}6Ch|`59O?|R=s@xu@^FT5A8HqJAF_qoj4WD@Y$3N{2)CwIC$}cIrIsg)RwK71H>Xx6Hz)tX5H3S4NEXdbE<^r_A)JSrh3wzNDT9ae|Mb5!{QG6q59Qzg4-WtJC)59$`}?0Pk>B|Dm)`zOT=n;c8Pfif4@T$Zjn?>2xwS|9'

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
