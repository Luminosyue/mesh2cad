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

PART_NAME = 'part_003'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/5fad3a288517425e96b5cc4a86ebfb46/part_003.stl', 'relative_path': '5fad3a288517425e96b5cc4a86ebfb46/part_003.stl', 'source_sha256': 'bf27694d9d2e41ec0626827e69317fbc8713c34a6103a7ba252bf663409c00d4', 'input_faces': 544, 'input_vertices': 402, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.4676342010498047, -0.4676343500614166, -1.2620370388031006], [0.4676342010498047, 1.2470247745513916, 0.604734480381012]]}
GEOMETRY_BASE85 = 'c$}qN3Aj|nm9Az{alt4k5w}KB6aiUXi1IojE`a)6*c7E%9-GMW05Ji=MNLEnL@|mJgI6@5juTN7R0yvDfk_0x1x4UNs{uz0Y6Q24IOnhWPrvHw>wNRgyze_-RsD6&srBA_{;G!ZZnf()H14m7S<=13sMe<&13BC@G`Ch%jvF?xVr;9Cqkok$KeIUgG@X5Ak1NXiq|B{mVzWUNV+U3?>zHnK!Qk_nwMaJ`JgRbBW&e@=MpX`~0DejT5o0R^A3L=F=n5&H(Y|%t7U_0pwn$G-{~!MjMIT<?Q(YxVw$J`5n{M2@x5~rwy&WE{e&h=u&-QY7u5R5;K5mFdZ|+^?<5A;prYukJAAdIVw&h9wd+e_&OX`o}3H<?X4l3?XPVu)~f6{H5IK1WB9PsG!ubqG5nX}jCsysY1q}MiIKX*l&eLikhUcb`!lOOExXw~&As}gYauYTh1>pFaUi)A()aOWx?PZN)hIeev$n;k8dl_lvDSN+`1FSlBp>!I_hcz&b9b^aAM#IxNxzEh;Xf%-pwyQ0Xy;AIK^vx*1)GaHEq{<Fl5`Of;!K60MZA2Pu0w;va;Ov25gPDT3B&;fScGiJ%kBs`*i?w0S~xAS+?&wgX~q4uA6dfKzU@8tSx@$CLZn=L-$2)BQT$KN|VKl=!`e~3rKBjT9=&#FG>NAb)9&VPwM@tFE?y~XeO>#OZ%iR=2Rel+04_xyFq6HhnoZSi<t|7$SbXwrQft^J?cy=&`tZ*lwT!^b}N@yw?VkEx#{9t&RO=_?-Xc6gTh+38z16|LjWMX&mJTJi3ymiV}?W2hf1uKH1J=O;hy4S)U>&+l-!&VK>lKJ5*EKNtM$aJbH=JST7a^BD!W?(_WkgWvS=NcZ{Mdl&J!vUpCPJNi*vpSzfT6px9kpWM0+-?Hsy$Gl!N|HSkC9Io@PxDoxb1pO>=U0?Ig6o=1gG6ws^<Q|!4{hl$`_A4GSZ>+_Q8I9*DbLbq4r`K06uJZI1&upk(T;}1q;VW!AneA&{D)aor#Lc!fFID;Y>iQe}`HY&sxW3B6W1Z)Dljgg5b$Cwajr!&Tw+{^0x$xX^e`Eyr_d|&5x~GZf=|}PWtDo6+^4+Rd`}3f9bVb!_e;%TTr>?X8Of7!RAFtw3?ZvP8^JBQ)v8<cFj*6T04%c<meUM)7*17Op6ECbk_2V(=wN@|qt|=aV*9>v}ZpHx~em8U7IWNmTTW`m;lJh`3<~*6@4$oFkU+uSB@UzX~;rBhR<>oP-Gj$#3Ewb}T+;CoP1?10dES}!e=^5*9*4k~>PM^<Rh40wjDi6;nUh^KXc%I+4xU2i#DX!nW=z#m47W@x%@98M;pXd8K4*X~JeG|6J_e8el{ZoXSH{E-q(0_fN&g64JJWbrpb<a^je@*=jc3zqn>t_|8SFDeA?Q@jSf4fhDek!i-w*oHn06Z7?iHV2v7Rx;Q&#yoKWeM|^-sSLgx8n865ZCx8TFK|3lFtYCo8sX<RNP4X=;LYCXIvTL;XYR!&y(*bTd$$pM`dm2`}3!GzEj)zWgebsMZfHSA-*M^+3udFLOe{oBpxOnKGy}D;|=u@kNf)hmJZJ|9uIMyAN8YnNxV%wd@mLJ$a^BGU7gQDKOc1QSzhBZjSnAicvf(KUxj$#yFfg{_^}Wt%%p$Cb$=31@24N)8S<-`{3a9Nk>d2Pcv^AtHN^}3O!qhO{E|J@{<wU7|M^usOFS3&kBBQDj2X{m7?0-;xOhIq%?mC*FW`*t%ttQXE5W<Ecu(=1;AmIl!xFrEpfBy({{L9qAH@s&qU*}#c3gFTc*3^7?yL_`A2Y5+oNLSco+_T1@9><)y`L}+p6}w~EcF#H#Mji1$O8-fufOAcAs#h!yif7;{<`kFHK15uapj4bhF`yI`~PrD$BXoP_lAqxauToEGQZ3Db&Tg2$LV)Df5%Q6pJhAsUSa2<-h%g$rmJ1tmbrPwM(c;)-!$X7NaH)>zQ6G)Cpf%W{l9R3+V@qiiNo`Pm%06K@%+3o_WO{YeU^LwA9&if8$DRdeK)!^f3;}6mallh&Kvs~ee<9lZ~W@M=k0iRPjr5c*=_yAJC|DATz247+yBNVZ?WU5f6epy9NPYDnQHOut_2INKKqmYM`!Cly)9bk>&J(5vHL5o+sNX%OX>fw3*2{U$g=1B{^ZtgbNlh+rgpx~yR+|d>)GccA5ZU^eOH->r^k+X$l`}o&-L}wl@5=Ns-ElX#~&YkyIr4=jt3Xw;qf2aa~wmysQWWNe2zWGiQjhoK=(stTJs4OCqK~jHFx&xYWcw-U#;-hH`=tisXZrRy9FLiJQiMF_CMeSzINP;CtE-122c3o(!cQisek(ZEW{^@%Xt0gSO3EIWZ_TWdo_OI3+()VwZh-GX3l+EFNELY8$408E}MQh&GK;JTmEyG+1{ch@a&m$-}IlONY>HzBUr~A@pQf7b<dyFbe>)3O~w01@$}B({Syyc_MG*n&&6T$ZEET@T4-_Z+x(GREuQ@#TF7zQeV*QUq5DpLyujl52i$X!-_yyZ4X%0K*N+Yux1OIYwYWZaan(SJ=a%lXc$WRizBb3=d3mm_AAPPr++*Ln(UW5qS$nn{ZQX43GxDCX{(|>RmUt$3&)|J!?SuCf-fvbfc)yuDcUoNEhxrX#T|d{6_Xh7zyl-uPg7+=n+qVA+?|&cn-~Vp?O5guJuJ3<*cWgfszDKsd!S^WUc~H{#&dx*dy~Fp^;tAh<ANRle7Ek!@7vbJ_-?o?V-7mts2l@%$eIM8Feun4BNpY8*$Kbu8cv9SD{U*d+cAgXBF4ec~1pbraF71y^8F!`iJTZtr6;JOkjc<KC3h+XF`xAKfr}Xult(D^sVVtkH#`$_~pm-SPD;~!A1wTQYuXq^e=haWZcN8x<=O-TW7jriINj_CL_aI(!9zs0iN8oF=+^Lku*>(dS7qfpMe^fl=kBW!<F|&%}4EU_#A)i$|<g-T4_Y=-ZY=4OR=Kyv;=>3DoyKTD(=OlI>4qaSwPGbG={5uN#C!Ld6{e*K8ANS8mZ2uF^No;=-&Pl9(!a0fUPr^Bgwp*4kKS}2#KJK5Bxc#!Y<UGX3<G_E?If>4{|NIultLGuXdX=1$)Z%$%aLyJJ56|UrzL&J$%yx%|`x)ni)=zLwm?IvZE5`c#2j>`yhtGSulFv!-{!zT-oS~mPH%~fWwe1Dxt9t&Pbbf356P(}T9N79vI3Kq5!TB)GneDzxIDfYK!TGb^bL4~b@DMNDTM<t>C-?Ef`+v3D_qpKQUh#ZzZXXkmf^&Ptvx=+!aK>T5eL;?Rc)yTgyp?oMVfBN13fy<t^$6}e4CD3iek8|rO}dvUGs*WdW#0OS`r*BdzAtjYJ(S{l50dxpkBa8G=DqPY*RSXvO7SSThf+Kf+(Tu#-bwdvw%vq#H;X6SyOnwSPTyBq#&em$rT2zbe{ku&q3!>$(tAVecUbYgVIi(fxW}}9f_uz7@uYiF+t1*hG)+Dk-nT|Pzs?8uvw7mNuCI5`>#vu8FRbfc<>^Nnhb7!cTR#c+(YF5y_t92AypIn3c=zU3Z$_~n<?XpHo$Wb6A^udJe@Vxi{d@T=<8obh|Mvhz`@#D?fWPkk?*V+g@OuD$=XBl*acs?ZvE=s>{&V5~p26xT{9eLe$IyR1;r9}DeiD8!QS|)s_Y&ZNwp?BMdlIX^t@QUKc3$$OzbCQn<%@q$lF>LX_zo%_eg`9sYlFB~@$fsFWjtLHuM#hb2gq~My-R<;WZUai`uioT-?Q}hOV)pn(%&!Heom`9JpBEVouBMmJ;L8F*>-!9{{{N#UZuZZviiMCf4^kQeZ1c<l^6Zm?1)QlC^wBID^kxiG=uwlKQ*%z#uU=zpPCJ8|G)aFS%>!R|Gz&q>o0xycaaxG`ZJv;@;vsW$ZDo2AC+=~{BKxBI)!<pN2i=1{{aR07nn!7LF63~%;!d?C~smO>0c<wFQ*{?F7rs=W*%vdg8W}a-p5jjyvjV%ts>h*HWS;%bStqXwAsw`ePT;#zl7<_#J16PDO1$FB=UEW9n2$rMP!*sHEotLh25X2_X_h!7l|yU-csh5vi<GUTf{ulEh6txZwd2DIF7$lZwvEV*r#ghZDxKm`?SOJw}WXlG40nDrtcBc@hxJyn3%Tn3RBd5Ch`l}AA2OdK+>yIu6&KiK$ZuHTqV+9q+H~DmOF}kYFrsQSBi9_%`GB*S$`32;I|Ijg8j|(3H^&%554Q@Uminwe2uw*zB*G6z7>P+aQZ_2m$XBhhUGf6t<7<D7a7F<?-aFva30#H+#FymWgKe-^)a@U#_6x(TxIAFdhO_Moz(53KiG8==}I40&=2Ht&K2ZBwg)+zzTo36k&oCW@DJ&`b;|V>_-pJB`qG;1T`T1$MV<gIa-DHl3z1(ELo9W+NGp*ZB4xz>B+`=@>Ms&Gi#E;Z<4Wp5XC{54t<&fOKChq+>N-#tb=^hIW&JtyiE>lwoyN2q+ks3MxsPpir)?LGrKQM!u+Q_cS2%Wz`6`Z~jAQ6R{gt$VemQmFt1oro>sjO0@=4lVL*33SV_q(0da=mWOwneRX<z!mI=;y^v&8$c?gp;kLe`hF4tO(J%T^+1h|H1l0g)e=woJJ^@bMzIQbvi47J1A#yM2=GHqH<1o)MWK@;G&nA7h*zbiStkBh>vw<Y|$)#?|em?ml9Vd3w7kUs3mQ>crHE>1zV}IEL-qN(|#^A$`~{>BB4|e|pM|7xMv|TSP|E{xr@Hq$zbC68sI3_4G52a|B;!N&WY1r+Lbi$4a@9diOJZh`P0?zn=EUuVsq5wbVs@TFNJg953=ODL*LkovA5*M{J<TY>}ZNgG7djG!dOYO8TY9e;McJ3rQ<Po)Y<karG6<qaM1@`8{o*_o&FnBLAd(L7$H@{Uht2qRr<_zo6eose}4|BQ}if4rg0~IF80CH>Phnw%N>|%sD_kY;LBHQ(4AXPf58HbN0Gm4~YDYJ_fLST*~?TM&v}vpOkVK=5Gk~AhSIERLbdoOMkFk!}M>|Tf=-W(UTz1^cI;Va<9leOmAZz_(YLOlxsz<6S+yG2W_X&5A3FjOcoh0l4ZUJ^`SGC`u9`!HzJWpKi1ty-J6JIJ-sQEO6rcM&N%9fqp!*AV-L17i5SK+LF8_c`&dT4C&$~1HeEz6Vg53X5ppSYW{S)Zna=z~`h%}qMW(Txp)3y(87%T^kx@)%vTh{xr_&z!F-%7?Ka=&i7j7hStVnH<L+}iG<yyp!6FFGqJmbRp^F?rX+)kv8$WiojBA!i=2H3N#Kc4wU)P+tx+CZ<Zh_D9JnsOrb+A?j&`UbQ)f$53#+m<@0KZ)4+Y_}uZYRqvQ!!f0p9?bkNIObz$bD1~B%ZYVm8FN-w<RFnc^zn0+8`2;C&Ja1180N1z^&qEs`lnJiMSu89Gp$3tH1mgu((RHSDQQEIgHsN>Td-*&lUR4SNFzKSQoh4Dn`yL%joPC;iS>6gJ)HG-h;$ISQ{;DOm)LnC=Zdst-ET$i5@{oH4sFh*?(Lra9kl5{A9qq8_J^X3b(ZuPk$S}L73?07$*em<<mcG$QvR)RHmE<8HfoRZWY*uy^a$1;lyc|)^(Ac}QkU3Wg8fcpBI^zlITp{cl&2bJgZhJLqxL9IWc^)C4`Y3A%%?~nksC#N8HXK-HlWA4>qTzDIM7ep)TeGQ&%QTp4yTVk)Q3IdW5m#i`H>=yzM3gwb8rvD;fSrTVv6|se5Q!m!7ZSJ82w7x!w&oabw3)%1JDL|Lmm18Pq>--eOU*;7qM=J*!`z*d;tRPa06w8$Y=_9M;{7!hM}x54ny3EIJSvMd*fo<CKUY3Hnf8nxI6PR*rv8M+Vc;e>aV@$;~dWxHch;?k?%`iojETfSiYWqhckZ>$AA>`W;kCL(-!Ljj?ta-500{v>j+NLp6dlZQ^qwJM192DSg)O2^Y-*rPF?syto<f^b!UAi+JiqScS5S%38``?q~J)q=;tlA*UrPirCPJ!;8NgD8TJP_xC*!cV*ZSAoB(BTo|Y_w!+;}zSAf&>WEp&DKFg>B7r2Oiz;D2Fz-8{EF1QSM4BAxA(}~!*wCg~d9^516u<jhLeKYQ<_SEgbymF^*+%q$|Ki~u0rJQ2{-{{LegKs>`v0ughV;pC39I(SWt}-<|<p$1AU)q$>2j+hrZ7wm6J9TCr*rhDP@6{}$y)4UD(a&>SN3^$)_5FxH%f7tEx^lLIdT;>n1@Ia0BXEoZlvb<*4sM{_2`RV}_zZXj_yoAj*R*+tekM@oapw0?w-xmdP!GHZTnW7BE2b!e|HP(-Pkm)-IMrU_&rnY}mHK#`ZL7}X^fiHF7|pilunhi$v4ZP7OdQzh#85YecDHcc;8n`0kb+Y^#JPHdDaznT;6v~Oo^&SD=Jb6!^W&*oNg2ht2G1JHI<*I%TF-Xi8{7(I<y`l(ZEyx~2XG+pDsU3;k>foKW$+Ymg`rGQh8;KvI1YFZbYW9LKToj^Iu)#g&6lkIm#N`R;8);M;7s633n+^HlX_ox<u6&kfNg!wGJO7leja7r0+xrd@7l)-mcg$uW^ga%mf%m|Uuo8193zb5VBlXPI5zOFQ#rQRY4-qA%oTVQ_!QdsmTjSY66Ivp4W{l8Z?2V_p>7uafPbav3+;h_ts(Xe+nz-X90Pm=d<pyu9OhoiuUH2hoI|-8QgAcyCU7Qj7jUJqw3$jjlUYBWdFc11&J?x*J@6`UG4QTRrYM77jZ4+=waQctXS<R3RO%^bQy<C+RcAbXP39P`W81S>zK3I-z_HFE)|1$694G9$Fc03QoDC^B+f3TeVE)&fue<37JZu=#p~QMJKau)_Dc2GMj~l`|wFh6D&UWB?49m*tMzMWx5^xi6EbumP9`K!GJq%^=AaIfMm^P*z_zgJJQPhRa@$}PxbsdQ{qD>pt*ETi04EzmT4V(;I>}ZklZmC)gYyZ@LRZ#PX^)*HRaY1NVeC_00juc;oOQ`a0b-|g0;MKA(;HNVv{WlFG__P'

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
