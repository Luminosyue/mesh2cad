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

PART_NAME = 'part_006'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/31b3720044ca458d90461a4ba5a22abf/part_006.stl', 'relative_path': '31b3720044ca458d90461a4ba5a22abf/part_006.stl', 'source_sha256': '586e66c610a2c9e61bac9e0666021e321de65b013a030e8e3b5a1e39d18cd79d', 'input_faces': 544, 'input_vertices': 315, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.07225214689970016, -0.14194796979427338, 0.18339626491069794], [0.1464834213256836, -0.07147972285747528, 0.24457457661628723]]}
GEOMETRY_BASE85 = 'c$}qM33N?Y+dfwiF^eP=;YyH1M95$sZVgp6*BIlCA?6^$r`75))I2qY#?ZLNln5oJ7?NXX3^%AyQ<aMttEe#){m<UdbL-sx{nz@}|6A)_&$FMr_ucQ_?>>9)bMMlzjaz;%1^+55UFv2%C{$5VgcVi1l<|Y&;)f0xG`42!=+8__NvVr}PF&Q!YrBq7CS|-bF<{`Ju>;})8khqb#ncO^VGf8H6&D{D9ouhI+`vIX|0sII*g?8Jc1ZN-L3%qdymn*_b9hh<^OxrT<G;ds3J%||wl~#LEfTytQ%7xd!IPqGE;3o_wv5Tpj~~kxZEM~XsVi@`LZ79&=$1{}c1eAAxQwIaOqaT2c^&Dme!Vl>sH>eG!GF<RsVmw{shjKclK#q}&s}t_@*MbAEiU6*QfDK6@h$L=iOe?Ywle<GUpd)E`rBsAhyTY>(%(|0QMOT6R(K=6)erN~KLPqrb9c)854V-NwZmeJH}^}7tHMLOjMHeT)U8?==ErKvHtM#v%Viu(cYhg2{o_06-TaaNh;4Qk{h}ZG^(f`yZ|?YJhtyZp!8~7G1^<<IFy7Xuk<X%JjCaITsaw{ixaiux{W6Xv_JPdPp>9O{Lf=b&)pNSts4I`ANPneS5%e3m4e|4eVBWedvm15u-S3d+i1x=^^smPvPP={CM%`L|pwzWGvC?1hPlG=75aRq^%~g*MME>8Ll5xx>ccLyc%V50sN7;?KS~Xkx+h)HxYSgvda)>izs*G>DzX$%C7NTD5mfMZGwM3g8#`W*i9Tl_Eq+WWijN`bl7jaJQMZW<#==aC{=+`n?##gS7w!7$c@?;$4;~99qwr3ztoez-D%q@1KZt-i4`F!x9i@y>z2Kh9bA@fmJY0#hTf`7SlcB5{YG#}$yviYb{*EWs9{0F+DUULs2pVlwZjL(ts`4Pn5@&xnwVy4}wYd!st&u`;oK9<2*n76i{A)m&(>@NDf_ENWQU2xQ>Ys>r)KliDNzh%uH#Q)e0^ItO?aW0w=r^lqDM%|KiW4nw~APRMVaR%|LrpP$f8J`_B>ec~!q`x{g9P9AR&xlhrS?Y>=VT>!|0_LGz4;jZ1HU;yUatZ!H#h~|0bkWt`XJs67)jck{b;}P@x20Z1K7STSlh`PFkIa9ga?+@)^{--I3h9mg>TnUMTQk;3fAz@XY@_bn|1B$5VV@b~Ep_u5oAg&oRLM5#YG_yN4|R`7f8~as)U_E=@UNV1H|pjiW97Qls$@xjN1HI{+#f6>*C9^*2<V$~upiFuhy7<wbM(981LRq#qO1NS7whoG0L(+t&dA5BFV;gB5A^%03;ZuONB*teo{;sJWySp1eGsS5DvWo0f8;Z=Kk|?GOZr=bhe5yUCH>Xpn%D=*j)4BnT#W0IALildDCh$&A)h9LU39HqH$3l$4?*v?9Qo{fhdg^d#JSddrPLjNw8Ht)d_VH6m4x{7M!1~IPTetKCF1;E8s}QxTB$3xVVGy`8&2K)q#E|mz(CX`HAU){>dmmOxDPmW>#mL1$0`M3o}<&SKA+|xj{AALQP)Bvu#cVbLA`>~5r67U#92NN@$(;m|M>*u-+#N^MfW^~eW}J%<i8;c<Lc;(bI{vnH|pjq)3CpJ9mIJzG8^k5rZ?hrnvOWVP9YyJ8_wS%tFcc;=D>emb*zUDJ6v?jXFU-otrhYwc^>oMCky>vzhpP+s@GRoCy$Gw-{3hr<hcCL9gzNw@^H>3CraHh`q@D_uJ&$teyePdx-#>C)YUS3kx$lE#Az9uA>)TW!1*;K9sZMMWy<*D*Ww;kD^u#0&QVfVH%~>sg%2anv{>jP8e%`mIVN?r;z1c-eK`?z-<%CS`(}o5J*e?Hh*O~?;>2VkPS9oa+xQ~<uO`CZeiOR?4LL4L&}h`F=Od}x3b&HF_Fxw78zo+1e(HCXakM29a4y_`Ep_XRa81T}`UCRZrtFk|U$7JT&%THFF@>aVt9S?J(XfbPM*Z)5$djHfx^34?)OY{q*#AE)3jORu_?Pr>(H#km;h(z@_oDJ8rEcDPAN$Y3WjJ3vJf*IF@hk2R-2bgNy``?WFNS~SVw_(;l|jEBq~W~t+>850N_pswf5rZDs>Cs)uDtjNad`i+B>EyB-qRex-^n;yTxG<GcE^4-B?fs~{ox;94gTlmAkPK?@PBs&=i_4w@(c(<zXwm_9CVw3JoAO1E_c7c`O9<PsoRq6h%?Ve#<4!CiTQD!o7ErS+`Li?`jOg*?^x%eYcF5IKjjGS1H&7^f9_zpPE_rCJV$q1BcGS0<+`;@Y=`IchYpA{sjZBowX1^l+$J8n?KbWSma<rfWw-1!KG)9k%Y1UD%lxaKrs90ryBqn~wEa@w^z@W$C#NG$vlCLclsGMQt3CfN8E@w(_z(9wE&X<NmAYj}G3+y!hspSk9{r?l>-rG$IlU?3gb$Fqa_bewb-$d{9Y@z7{sj-2zq0b#38U_uXZ6}J<as+?>RQ!-$n(dFh!bksE%m8S@LX^G0_W7rf>Kw*Yf675w5Ige8kUo~<4$u~7j4RZ%=4ZAsas!+$8#N(hVvyMSn5iF{Mess_Lq5Tt-{goi7;75#j6L->o*OgZn<efzeU@k-=r4MdqiPh9r`Wy&(3X;=aKvSr2m|;r;NH*{TiN&T~n~H{uG5g*LWO~`Rw+@{kiR6#7WP=JWM{0bD_ad=n3_(KVLeDI03_<SHFyX()}g&tB0d8-ZTa4vr{tmx3v?XUr)n+>)4Kcb@(KVYu8lx`z*qJAbc9~zmo|4{3ke<i_Jv8lYhfL89fL2{5%hOXmR8@vmVZit=~x9?CXtv@7yxP|2-4&ABXQS)=}wx8vgdW*l!=*LY$Us_egxSTiz$NFDkj{>VpW}V|ngai*1y;t?!?>4=1K&yXgEL!+GwgTenNyGVLYqtCyN*8+F@_6ui%xa*=-xP3n#YKfwRDi*}=K`OgX56Y}7%EIkc<#WTzU@5$z=XQXcK6NLQxOhVm%cOZV3IOLhr*hROkZ-_X~bGh4N#M!wE>y78E(&7pH=Pbv4sgy6?6VJZIyiFPj|JoT?|Jq;3)0~d`822S*g<HD(T%eC!w@S|nn4fX(Qn!3F9OuZG_E^vTJ*2MIzJ)y3HpBchE(U*}TG07@f>SpuTXF8pyMgDcOew@^dJWH=|5@m<eo|L1pUO0@A4{D;_-{>uesBfm;ay0&%le<t1?&08aH-oqF9_Xj3F>02D|Ia}2yv=6!#odeEOp0(uFxl5K%5FKF|K94*iY_ngMUVQ#JTJy=gks13-`e29vJVTA-K2Xt-<;7>mcMG*$wATq2n0W`r*j`T^^phrTLI&zhva!U^e!{pEcZne%XP1cz?6Zh`~AKKVqN6hF&rs=X;+L`nA*@OJdOP{GTzdlmw}3sfo~I?N|>Dlc3ihkMWwvAWp(o=p`m%9~<`r#&!4z;ztEz-#Z+Pd@MOqR|h{oXso*><eb!P55Giw?gMJM^YEWu33}<0sPFSjh+nw{^gbHq=i8f7R~o-UeIM9Sm%jI;ZuLBlItHg8ezix4)BGytjqi^R<th68wH9=~pW2S)A<sFT5od8Hz8`&kK>AmBi*fNhvIQ-Yx-B&w>v><itL|F`=huZa)cub{=$3-e?|h4V_9RK&(c2AmN$!C0Zm^->w(-bkeG>BN^}W=UfC<pAwZ?cOH^YDEWz5^qONjG!o764EmcTzL9pk-u3i){ag>_rm56}D87o~2#oq#<3HY3lt%gA#~BfO_<=#A&ydPVAgpTDf5y3s$wxDK7qg?UU+hVi*m8pUG2vTe!4^EF(a*V-A|sejYeW2>cZ@!b#o>~x&(mWjBBJiZM5w>`L@bnFMc)dQ)Uhn2v-w=D$g{Qh&Ps~@e!{BPThdES&yll_c*jW{Phm2s4b?ou~<jD!C-sd!HN7S>$qb#4OU=aiMYEwer5t;SH?XQrE>k1}DNuiU|U9_BA~M>|jC$?pxU(N(0bOg(^k^E`IasGDQD<GEPii}`O~P3l@w3EWHTwU_rsC8#?3{rNQ3bJb~fqi*g{ANhQ82z4(S0zIxgblyX>$Dx>?`DLM(>W6iHrxxac`?gwQ3;Yj8U|h4-KyMx8qAQ=q$UN17p)ybFo=C*MJ_h+8FN}NdsP0m?-d>OUYFr5RnY=II|DUONPh8mt`_=Hdn1}BZ@xHvE3D(2wZ{hE}|Nprkanh5JKlcY^N*KPMd15*!<4k{t_jjHn>f~Zlx2#A-{)642*YSq`E6ZLP|J~$M|E4Q9reQswt|WD(Nf-E!=#BeoXf4Ell7V?xI{^9oQV;&0jFkTB7Z$9~_~ue~zE>(6D<i&J2dP^Z{DOO0&}-y5z7O(QIK$<81E;R~&PAR|IO31&D|NG52>kiGfbw)0;yd4?<1S)7#3evCC*nP&=8vd*<~pf6-o+#S>|m_V)D4JVsjs|;t4YOC7xPZUu>@e<4k(ZPs?!O~PouRmj+WzrI8C$Re|0nFv+ga-=Y{j=cV!m7kD8N=?+I63LBFNm;2!0(1LO5Ba7e~!aR~20wmF#3eC|@$&YpySfx*ycmWF?PhRk0pTo3E8OeN@(TDjCwb#I6`oy%Zd@pn4)StIDttC0VWGrYI7k-GX_1;l?+4f{;jc2akK@A3EVHEr5U-Tdl4=Ku6wIbJol2jUm&jC>+K#J;yM8hXq#8Q+qafH-3ZBEBu3%R13o3`IWOd%(Y`C+7LpXvFbJM*geMVm+LTM;yMlI`;uJVIuUokMaH$RuJ<uKt=w8{IDL*2VuNTrb*qgb~eVv-%Tuq*1@0e9hNuwk^kw9(E0wN)#-)tuHGVb=X<)A`z7?|doZry3lWF+AI0kc;vCD>jO$Rz%fxv3o~T|JV{h8g<yYh)qnEW+%IQ=$55-G~i8lO%EdQV=f8)RZggi9jfAte`WJJXO_b24)CPn!`w`#=F<TZ2)(5(cmIJKI(mC>y}u_F0j`dD7;_K5fg`7Pak*X<=Op9xw49SiDqR{`Erz#q{6Ch-=zz}w^k?~val&(-a*ZV%b_ALNgSx#W+??-B2i-(lQ)wA;+*F8OaX!SB;<GcTdPqwhP8?Jmdq#^8U8nlLy1O_<>C_*uaV(A+pj0`rp>Bp37jigW!Z@h|c}$xZYV{w99Tjod{3mUVf-+yuTQf6IKF<9KJ7hx^R^1#9+}c$54sx#;I6=i1qCE_2LfZT=)aHst@9<9kK^n)nBKL5|H?(|goja^1WjJ|I7%+ZEj|(9Tjjs@qSx{Y<+`?YeF^bUQ(`lb@phLE=$zfyc-N9w$FYo~2ukZl~GzS@JW)Eb=qtcH(jJ<BV&k9b-Nx$WPJ)&!!z?UMKjsUuoB=iLw4-@IOjT*fsv`7joxkukrKO$!`!H<TuF0T%YG$UnE{3zes+W=pc76)@7RDmspo`%<CMrtHf*MzjBPf5VOh8v1XTu2gxsyUnXW5`psgFS**=PVvZsI9FFfi`32%x@*5nRv!-@xVk|!~ub-Hc;Nx^l)@>DSF12{wR_Zp4xRHFbZmGJBB*v1D;b#UDhmi{$PA+f+`C#%Py3Nroj(yK1A4eQQK8`$=ID&ix<Hpj4GoO*<qiKSVq77$WBl)-QX`88uv2HN<52Ge*6aTh>-1*r}{QPF}RALHwD!G{J?>N`1iOJ-v$=4H8$Ws_=Jx%a+tjludwVc{U;wJL%ImQjdQRK^6vvtJ5<m<@S6Nec39l{)kur{lSa}4><;rPBIUqzftp31Q~YZ^;Uj3u6V#WN?t1NFVNwr;hEbqqX$ZGrX3>#-d~3#TS{AlreAA$TZx9a>##bq(=^HK5jj?QmKcwJ^48(L$*u=wtXsw<WZt3bdtc`<q}@Owa_c#I`^)xtVQuS|MtJi};0z3FLmdCF;C_2`0EgTtqJV5;-K&{7mor_h$@0e!dc|0{axG82Wc-Ti7Cwc@g6}$L`dA&~2-3YiNSoh+D{Q<SU44$ybmsqX`~EoJa1h=ip;PKf(mxN-Re%Oz<tl^5nt<U(1++&m-0)FQwyC9ZM3QkPCc9E=+Jw;&XCgf_oA3$OV=)ftTXvy@{UW-sC<+FLEF9a>TOa<;cs^%5n^K$wP^v?@(e9>Q7mlCqx_h6Y^)o739yzpA(mnKPS(lEn^?cSS!KD>Nr%lg~a*fLSLX;Q4_GR3A~sIeq(7)EsR){7D8>lA?{EEudM$qST|q#7v^U|$g2`P$UW#=l^9GeFp|6~c?hwAA*OSmFzy)*3|zz!IW1;xNecKvqI0~9IWGc}$OV2&zJR<i^B3HM`3vq#Od?NWe}aozJNKuhe16uDSK%{Ng=^8t&1{>wcD;$BU5NIS&yC<B{!{j|hCGbxuE;-X8TJqE{QFR@pLsNAZN)w>_W#;6vDXKg-p^w&=UMPb;(YQ*t`%oZoP56W-}So0dE_E5k&iPsBN}-O^X#EpPu+Uy){Sk!yRa>IC$<Iulx@K~vn_a6wgvCbwv!8tBK9Wl&30d6G<kn=p$%kP@Ih<~K7eh(t!xY4k8Q#Gu-%K}>qA~$w*bZ(NZy}VnY=%FG_fpsG<jd57kOXu-o(=6y~(49#mS?{yAunOcPH;kEJ)s!yfZOBd1vxZi3P|%CGSLZC+|ewg;<2V3wbwU3G!~_J&2{qdyx0!91h~VRwu7P96(-!JdkK54<z>^_9OQrFGuV{UXI+G*ps{`^AX&WyacT%wW4enp?OgAVB4MMM$Mgb=SEb>6}I!!Ow>$l7o_E*mXGbiv_jMhv0a>2j9M|aOOp#MNfX?QT%Zq4@Upau)GD%FnO2orRkj0YHK_%#el>};$ZN6ftYa9pFt(j_451dnwzH1as8wUzSw~-LzHEEb%1|rAb}5=CHD@hb(gbf|sAUV9;LV6`<ju$}hFV%^;$IU(Et}8;Z)~V#W18Si4Yh1a6Z}I%EkC3Q-keyHygB(tL?7~x$Xgj|*@`CkCx%*nLKD0#u_k$2^7e*Wwx<c+!BEQ%G{HL>YT1z{csoNa+tCDXW2j{tn&7PswQNlj{9{8cKPI*$|53LihJKGQFM)>*c^>9C1ZswHX&kq}48uHRaGnJ2GtApQ&a1$^hI!u0ItbitsLO8FP2f&L9e1+M0@IZDbr-xTahvjfoe18TxLtX_t^{vF+@ZW*hk{#(yOj6qR`6!TJ<9uaE_e%Ky7K<HNatL4Wc_}m34Vy!hWrqDCb2bnCiwy4$K(gd_Y+%^w`9M9tGa!u+gG|xVO#KNYzsbvZNX=<?c@Sy6K9dnVtYFAYx1e&LYvIC;FH)E{0p`P|BP+H$FnW?f7lj$0^5Rr&bHta+5U>-n@Ap{Tc~c~#7J_1b;$+RBNy0+Twp_Tfepw7)+ZNOhg@I;xxm`w0)xo~Rv{NyiCka>a)BR^3oK7A&`d7SpWL704CmNYwu8t+iBrf!$;BLWY-7sj<@P`Q7sU7fRC&-E|3l(GKk53jlkt-u>9PL)5vpUG0^&T@H|~7$%bm$$#+Cm9w^)Ra'

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
