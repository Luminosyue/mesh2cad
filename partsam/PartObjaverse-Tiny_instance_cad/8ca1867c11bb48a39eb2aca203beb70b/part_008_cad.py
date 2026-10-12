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

PART_NAME = 'part_008'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8ca1867c11bb48a39eb2aca203beb70b/part_008.stl', 'relative_path': '8ca1867c11bb48a39eb2aca203beb70b/part_008.stl', 'source_sha256': 'fc6a25438b95edbcb1a759a5cc0440c5040eea91df040b2a063f7a873ad5cbcf', 'input_faces': 729, 'input_vertices': 475, 'input_watertight': False, 'input_winding_consistent': False, 'input_bounds': [[-0.14037039875984192, -0.2863118052482605, -0.12978513538837433], [0.18888671696186066, 0.0029137730598449707, 0.4536840319633484]]}
GEOMETRY_BASE85 = 'c$}@A2Y3_5x`t<s>BXU!P(%r)*fdiO1Yrox6o($F45k_k7zhbf3B4U0Y9NG&mQX`N?-CeGmTj6Tp+{-trjkMub4YUT{+e&3-O+HLd(XK(&;NYyewrE0{4+ZmviqEb_<Z4I82_uz=9I1)Qz)7-iejt`dv#Rmv~eRxO>K}e`E`vw=lAJP=$fAWdL+D}u~*rw$fQwIN2W%`S|ZzwZW$S6i5xvCby{j-%J504Nu$W`lsIAPDBYhrHgWPO{kl%m7R{n8F?FLXb1eVnUlF|v)?I&`b5dVg&RRg~SY7aLJELzYIML`ks(f!Q-~aI)lP}7{xBT!5_m6**MrvJaxoh$r55}}J_>K`hP376Z;$|P^h0oTHIqUcD4P8uX@0)7&(`F|ceQWvqXN>)~KPYq0<fH$VuRi1Llzg50_LV(IZEbJ+ecSLUCg0K8#r<^__=mfay7E5d<4ykMw8_8i<^9=l?X<B!E?ew9lP~f)rXcq-lKsAY>)X5h{hXoQ_vfc{lF4@@f8#IjTUh(FF`up;JMWr&<Wu;LuBCZ9kJ9|@xat)4x9{6f)YOix<m$U7AMFU=R_&`(e!uNf-cI3PdH)+{oifgst<kQ#CLi-9d{@MGCyn{B^*U?zkssmvs$Vgcx0K#%_Qm|dw=J@`{2G4zs=uE#Gxs<ZzRhzo(^%f#c$(k0-=2QRsq*dp-c|XwltUS+c5HjovrYZ^;=?Qc`(;k%ai_w!e_qzE^eY!hSGD8%bHXK~Z@sYLifX);he=oXynXkv%D3h@w;Fv%;`YmQ?R)dHBP!pzVAC2?JEih*KmF`!m2cnBa$Y-y?|4$;oXU4aG`(W<S?=c-{q5&oH|0(E?A6ipOn!8=9Dh3vKRK)NZMPbxwNv<x^e~sox70sr>W}s5$!!1kemM4|Q|0Gu8))=hA5HSA$_IR@Jeyb4tL#7gkp9CD=|6nA|CT$QJ*s>PU(Tm3qPAN#zrvU2SNQV$3SXXImvdo;YP|_RWWDtpenGjO;mhmU_x6)?)qP<fl%1}+AB8X9j{#r0AB8X9kG?K(=l$iS{UqQ^`-$-7{UqQ^`-!8%iF2xP2|uvE{ZidO53V13=c;^GKEL0$Z|;_%@?Eo|a*V!h?F;_>&C#L5d8L0N=CbK~AK$-h>L+|li+B0H(KFoDPT{*oow#CZ|E;oo-}rsgL8roZEwDL^zALU3-ycdXKdSQWogb%}{B?bD`221^(@y1Q^uB8H)7EDB`|rMV%&GA08@^a<^c~A@WUAT^_;ULX9(k1ghcEY^rImK8@*{jXKh|%TXQ=Wod^!KtW8E`U^XSOCe_pj70=~2!9KTjQr&@2qm)D!G!+e)<-TGF4;IC)>Y{W&CZ^_rl@B5a=DSg|@re33O_Z;K%yFVgR<-3x{n993+@!U^3>Q?#o!>%k-KeZQgRQ(aY+#mLREN{ox!lUwSt=gH|x6~|}qsjw2@zno&WM9+6t@3>f>t>tATPc_O1($eKzOCdVa~|5x^!tu2ZQM$KW~`}w>w5`)-%@&pN9h+}=5b9Z>Gxgk6>gPp>GQ3rynP1a{cm5wqw?9Uv8M8DPn|4PdEv|Dtw+jdsrn;)xj)u7Z+VsD6}~iHYsyDnRXzj0luuuQ0bbR7316Ns+t_HYYCQ;FUJus4t9Xs~dmulqN14j?3142HR?ByO-`e)TKBvNG&A;BI@<Z+y`11W?&3=%nx*vrv-;ee$Q@MX+=6<Kbcb$HIm&y;>A4GX+f3Q}4;!%zle#m&?hm04#JYH9p$77rqSFM8nal4*0x%5BzVt)wuv!3$b$L?njI2FD<^43n3Z_S+RQMU7Pp4aGGqXzqZNA2PVoeJMtd-hh9@AHgttJ-0`BeIRYeOVIUC*$@Uaw>e+z4@C}K8xL$p=!tW>3viCuJO(Jz7f0Ruv6h%|17#u>AzSnL)DJsZucD1xY|GVs@fO6+<w59+84guzHj}7OjUk_FXu=2a(;v_=g0cnMUQfR;fKsG{E+#DFVC-QXS7GTKH-O~PxvA0Q?w(kPgmscZsq*~U)(P&ysY21EX>PM`L6sA`S1IZ6-wWh_N~bm=L%M2rqcIC{AKq4UaV|i_;UN!dDE5swAXsbe;;e+x>dgYw;fqV-!|z1_h;nusC?VDsiyMQ1P^aNVvk$p+Y4VbmA4N*%FD;s@Th!tsjsO#OI^#)1B14?Rlfb~b#wVb3wb}QSN5oUd)^>(|A$TB-`nt<Tjg87Jz^^FiW$w@FaFrA@_j|;o60+WIPX=J7rtEHnts}=><@goKlX|{ysGgEUmmaRz*?^=pTd{(>B~s<s^&}h@_e}lkMye6gYf0`zz%lvs@9wE<@IJ?+|jFC&+z5-Y~6M!(|EtjzI?y<YHa1_mM)9;Iu$;vAF)T}%lE19L-ql2et7Assr|rtBRXTZ$`9E$;LH1l<M|HC{tI93zwqV$3qNF^+1yB-PxvCA*8a)7pV7@Ps(fFAlKebiOH}%f6J@<dpRFpUY{&Z5uY8}}Jy+?o$$94fV868`wo&?wjaK@;iY2{D|5&WKpVek6`y+h0Ki27qIjV8lZw$#%<wy8(eq1+ODBE!yv+(c5ej@u~KM}s=R;e80{Vx0Beh+-__B_5HKFM~gd|$P_rt&Q55#Lvj74xWk$B6Of_BVdX+o?Rwt@7DlVcDkjv+4@(Pud2z%J(h#)YQKCopL-F;!*msmCXHLbei`+yQxRzJ9@^M+s|FazxVDcx6*I>wYh!#PKoo9?2GeKpq<QF{NKgpqCG0#m9LvQpZJ|}Elu#KeEX`}rt<c2gLyt59doOEUtOoEyzOuwo}c}BZk5j_%r%$)t%d3LUG{x3*UbHK)Hj_^WMBMV1m@lTmseF@_;Ps`^|M#iAK{1e=Z~9S)p&(3kCz?4=vC!Y_;NnQIYFK;;mh;o`r<>cYCQ;FUJv4&Ag?#!%j?b3Yok}So&&zTo@=LgmG=vL`F;`S1o?gp_|pAoe`}yub-xQ=zTX4q2WdYMzPz7U&$QzGm-Z{+%lnmMP9xqQX+IRcydPS-mNT8NWMAHIZI26^&WExu@8|YzKbwB91NrZs!_OP%qW7tM>!K06mA>?QBz*bz$g<C){9fV9zf-ob1H3=(vwNKipY8u-x5}4)X9MNs-+i2ytY3Rf;|-k0CRA7Y_WaX#t9<K<OS@El$hktC)1-5PrA;&Cc!e*ISNQUH1LdXh+E!Oq=3n?B=cqXqmFq$H@_GpP(s~fSydLaxADjOBl_NZg|9c(Jr=I1DehNSMe5&(dr^^4e#3q$5o;!rL!=F0{Up&uZ4f~&Ts{9>sLsh<b4ie(yIY?k!crGT7OFaLwSGs=Isqk&{Yo@8ni|079FP`HF-yXMummm1OTjjHJ%d$-Q>D6D^PuI)Ec>C)sc~rh-{t$CJ$qxU2hxCo^m!a})2dkU%Z>iPF@3W5kGgQ9shBw>vz2bRaZk-D%-`2V3MWgSV^c#P^pZD$srC<HFsXyX5pd)9q%c=6`p4g}=FP`^>_;}tI$p8Jh{QUFBqI8vSul|#%|JJi(c==MrFQ|Nbf$^sDY~(qws=V;!^1cpxysG{PU+#~1jw$CS;7j?DpNEF{a(+IJ$yCi(z?bJsJU^A!1AKWsSpRzDR;@ST%j?Z{bctKFo`o;3XUFBrZq@xFeEEK{<>qFn?mPRqEg8!D7ruP|is!lVej<E%Karmc%f7syi08s`KgIK3dH)Rf(*7wwM-K6&{WJKy*u4J-d};repF4-PW8VM8b7%SYNPZsem>kXDr;y$^6TbXjS%{DKKmzSZ?}^F2crQix@_S#xm*4x6eaq0lvyA;0?{_(hJk2rs^7~z~FW&zVe&Btr$f=i1zVu#}?2GrB0^`E_RJO8hFB|>9dsE@D=T*L3UVfiS_T}#lya)A5zI2r@k4t_(O7`Xai1(T-5wkC-{E+<Py(Y)$*W4;!o=5S%le|9V_nl;4URUz_OCi3rZcXnaC79l#9`^asoBL`oMp2lRVWSfbuTYaoe?rx-P>*Z+zj}qbMUz(l=_}NyG<^(uoP;{Tq^H3r!Kn!1>Cm&_>EPF)7r?KB=R!T;x!_gM9PldeJJ2iOcfk9gpMdv)KZf20e+)hXy#qc1K8~?WGmMe=6!bOlDexKS9Pk-%I`kjlbg&z`3G4=EL-&HS!Iz;QfiHt^LJxy)f^R{OgO6ie#KZLXU0+*I80W#b9;)k~y5@mL;F`(|L^;y_;IVrArGKu0N8<W@J+|qQqH#^qIPb=1Q#7vRO~Lmh>M;g75j+N*44nertk->;@xGAuH}sEqD0Bdr+6mXFqnwj*O?BTvebND_N8?CBo|4e^F!+=+8skWKPte9z)F(|eeD?s1Zve(N0{x^MQ_csYTprrkiTb1yQ70K=9}7(ZhvPF1Iu=ZIcccDp<a;7MPr*1+Ft(BC6T@7OK#myloP;^tjC|AeKAk_(V-NH&nDjW9^fZ{%1tz@!Cd~ws=79G@KSmHAK@gun5T8L1pF<F5Ac(!t9Pn_;G36dQ3QRf<OqvWPO#zdR2a}EklO}<OL2b|^a3ejM>k*3}ZUcQ0+y)#6?FfzocY*c*cL8^Uz6|aLj)(RI$Ah~<6Tn@;ouS>qox$y)9l-6ut)Xqft--CJ&A_d|G0=wK7;rSSHaHqwA6f%kA6yS=0oMaZL2H7ezzv|0;0EBP&_>`!n46{u;!)5x;8Eal&^Yioa5A(DxC`bZ89|%^jR&WI$3we<yJ8N;BZ$XB+k?k~lc24^t&#U61hEYo1Ga&OL8HOZ$n`J;@nC2@@L=$8XcRaK`5lfRPJ}iEH$@(aOXyKbk8<E*xGt&3^LiA876umu7l9T6Kc`0})T@L##1-@?t4B3x6>v3hRcK{!Rd9J|8E|nuN~3?J(Z^zj?=A{038t}B)FT314%bD{=jWi6z!7M-IJhFNsn7Y*$8hwAK`XQ1AF&3l0<MC(8pc3%3P8ib^m##)A<YNYzziB@_^vS24?`Q_s9OPLD<Hr55Y<q&8uA;4sEYbk(LdrZ^!QAVuc)rxi7-9#>+w(h`l%j&=<%B#KkM-;g7^{i2k;~CchGOZ-+{lzcZlyJ{S^Ee_&)S5_&)eHg7_0XZs>7ck899e@HOyN=oRo)@MQ$?B|W~>!>7mR2;v9Od*BD)JJ4I;JK&poJl5kEJ${1z2>uEDJ@i}f_u&6R5I<x*?_v%}|HU|mf&XS)pMw7e|C5>LtFgxO`xUq$u4mGk(D@B;d5vG!g;v+2zQ*g(oDet0^+G*jbY2RkIx(n2b)Scp2fu+bRQ3%P{GM7G&l}~ExH7KodMwbRs>ZdB#<`vzQK&~+16%`jiD|y5+&yS5@at%|oW_;fBc{3Nr189yS`FL<*Q76k6Er@rG|$96aZR7cqRa|hr!mgWQJ?r9xF&6>ai%&CG51!qL)YDO?T+sx?F;@1pFM^qfcv69bWQVb)A$-79Rl8^#|}LvYg|WboX6o_4+BrY^}BkR?Rx0{6!z;Vjq?!f3)Cj@a9mTF4^WPDlE!%g)^UFDcwAE-wxA!RgEY>xN3_=Xo<Z6k+*#xM&LeOyTvM4AC`Z~3O#9DE8sB$F+k)5Vu}Y5)8rN1D=MDI*hsKq>9{8R<db|wn2YwkG5A6Ydi}8M}WSrX>`bXRu+7(RuDz)`9G#<PTb>9MaMLik^^|>{)1(?Rx7Wr!nk9ZU6t^@Zme0NujuPesZ3%RDgK7w`zJ5YBMxF71oW9%<MJAi2n@tB8rc*Gk}*8%Q<{Jn&_ZK18eG{?P=r(VcA@k-3yDsT(bq2G%aG`@F{*4Ki+ZDLO}?uS&SCd!dUgK7Vw-y8a^A+CaJ+B4^3-z2T5aemgmO5a0!WF)jMI1*f4Gw;2N8Slq@#yQ&1KjOyFW?*WEeiP|8GZJmwMcw77PudLiXdKk%7oau4G`1?pUln-w(Z*8LCyg<DcQcHy8OGL7`~UmxAfIwiW2p|0uHRtl-<0Q3w+gf(nEFJyp}B5|e9`rM%-vjYP1Jc#<7W#xM-Z37bxDn%C$57_;F`*mMmf^5;3677bI@6XxHzt->oG%*f*RLi8s};FtboRqyaM>12tA5I3xSJ*3quQlXX$n4G2R!_vWET<mxPu9Q#*7HqVrHuv~dY-%tn3EGN?!6D26;0L)*{6r<~Cki^IEyHeN%0(g?$Mm%;eTU~DDOPs%anycEh^M;ouAK4~G;DU7iffffXlPr0YD6oz*hZA?S`X~=gWd|nXaD2TBYN1rG+G}k4NuPd0tS(v|B$Tx8#jh{v6TuEF{3!Wv#xyN|sp)yTTjx-8fTjS?ZI(rf~z%`wVmN0%cB5k5^wlnqFiN2?T9+jZwz?HxjXjSksz3w8$`$8IJ=%4BgMrU7Y>kiZcrn+yUK4}fqqj5Aro|>TTM(`<TG{y$-=z0$7z6q|Ng`WRvU~HAO;2Dr|E}sLb%p7nz)UjafwV`#u<WufxEEaeV*t5@*wNbYLv<bK}azt}o8F{~nIb4SMTZViSi!-S>pNexSoek;V2@k<-aQ&?FsyL_q!p!H@jf|fc-vjs7`1N|mz3%voyzclOI<Izw#(_J6yFt5y*D`+orM{59Xy~6fE0Z<{Q#*97rGF1~L>qMdtg|$Yqc`%@8*O)jPdTG8_JsE%d-mBo7TN~d5-iT*51IK)PIXtKK4~24{9n)NRChh<uSdS)@VPk0_r=(HqED0?n(H>m7hSK#+-(GRL7nA#EY@Qsf_N$PP4H6iLg;MpLhyX(8{qli1<*y{1>hynW#A>?70}h-72vhdx4~<{>!A+tdhizL4)7N6Ht25fHt_q<1K{_;yP$i(yTBhHh_^#`f=Rc6w}an<ZUnyv-T++#-T+<)T@GH3xgqxGbC=Ed_mf^^!Tu2Mf@ZN`pNZdxx><0H#M_|fSuiKWTcBrIFo(qJp(j}|=frEFM_F)=h*v-lvf!K&FM)o@f@^?y0dy}5t{LL_&;u;E#)ua}53%5yBwh+V#)4~@cqQ}{3$A(Mbx<dmf_MWoodxHJ_&unH1?QA_JM;t0e}A0^GJ34cgZKsLAn*&|y3nEEy5J_zk>Doame4WamS8J%BG?M<1f2}-1nvb*1@{8?fldYY0r$gLYB4^({@?-7I^Y4|SD=l-uYiX@TY!gvM?l+wM}S8|UjmN?Pk{CWPXJGX_6AP^Pl5IW_rth|r|NSyLko_Jcp!8Zn1Xl^)DET~9twR6OhG&n`YxD)cntJIFa_~M=pir#@nq;RFa>cc^aPlKcq+y+0OO+|eiix(n1XmFbO@M&cph{Fn1VPBIvPwtycs$HOhLRKItffcd=NSXOhJ4UIu$$><07Wt9r{f=haf%=T?{@C&VVilXMi)IYrvV{Ea*mX7Wfi$EBF#P7rGOi3%(BB1HKNv0X+b|0lo&^4Za4x3f%#|3cd(+fG>i*(6_+}@mg4!e9!v73k?3z+GVEy^FX<#`4t&s%}#n-ffr^H;`7t<0v4wKk0vmho?Np324vGDsQ'

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
