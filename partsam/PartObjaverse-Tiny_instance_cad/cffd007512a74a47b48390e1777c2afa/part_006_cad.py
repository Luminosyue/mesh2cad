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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/cffd007512a74a47b48390e1777c2afa/part_006.stl', 'relative_path': 'cffd007512a74a47b48390e1777c2afa/part_006.stl', 'source_sha256': '285187b7b6e9a9aef89dd66bc2f82d58ed0585aceb8131438355ac9bb7f8fd18', 'input_faces': 620, 'input_vertices': 376, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.31873202323913574, -0.4608367383480072, -0.42413610219955444], [0.3865852355957031, 0.1339038908481598, 0.41401758790016174]]}
GEOMETRY_BASE85 = 'c$}r233N`^+Q(079)kv<LMVcoL(D|YVu-PZMiL|lLKEfoYAaegE3UCEZCa|Xp{)+)NMhFEmR8Ma6`kmGTXnUHd!Bdy&VJv$^L}f6>-)0SfBk>?ciZni&w2JfCt)={u1L`^M}5_HW){71An$I+5tVhqoS7*ZGbW8o$!wZF{h<)2f-jdZ&zB4s)<1q^h%?if9W_2Bb6iGL`^cz{scoYgM@FSi%b1aooSrx>V|<F_J(H(ornq_L#N_EI?)MF%+r%`EjBeOC@{!2@<5y`}!(FMzbH$I0-qgjl>~3?;h&we?RDQc#@O*KmncqE5<!u@V&wq^b<&nJ~F>^k*P`+)PnMWlX>nW789-TK#3cemMuh=p8c-E8D_hB=)=WjA5_<FqD9^X76_<CC2AG|(ZZr8`l?fS%w3Vy%7eC#vvy#9yI%74$!J#i*CNS;-HgD=lI_qfVexAx^pIVXeWdi<GrzC7!bB3pgy*>f^z9vj8@eb1|T#y36}xE?##^KV)1%Om3ts`aPd44P-ndEChL`p4f2ntS7&w^kVIJU{k!&^$Ja`PaXw@<uz2@pfKle0Ym(LC2GO<DHeSs_U8_buRFF?Od;a;p=Li74L61)^Fu{{+Vy9c@{lo)Zfm%`a9#d`||9e`+arGYY=`mSe}$K(HQUVlWJ#!<=MFt)cE8bMxFEO+;uiso|LD?XWhTcsIybA`q^N4;qeW(1s|_+Z@e=wU#)ZP9JBsbuKTU;K2^7@$a8`9v2$IYo(I(Drd8Q#+%GHF{nPEB$}cS2Zmi$R_4-Sm_vOx^>Bf5O+*?mp$VD~J)iXPc`K?^n^OnkENA6YgR;qJ0Se|qu!5FXmp<Law!E$@N?uRn<&IZdPPpa|G%}Z*Y<EPDjwsL)*T>r-C6Ft9`d-LnON5r<E<H_}UzWY(tc}10Tf%UO-?|PlDeo^yuO5Ywhzn$y#ocT@F`InE4{<L%5pPyY*^Q;`WE3n_}T=(0i632b{uL;Kb?Od;aU1^oSx^RcFek<4OUsc|h$42fj_luS5{(Ldimq#Y$8t0Fl+vDx?$IiX;$IG)0mN3pAJJ<VbWd)Uwy}mPWzu37Rzr3Q#qqiF8m7NzFKce!spySE)_$R`B`T5Od&HZlWx;}HOt9e%TG|v+&*YhVf^yNwIA_|QCW#xK*4Qi%7HzLlwzgDi#!-37!eNS3#?icb%a@}wJTln(q@j1r(fSv2-Bf0%PVCVLD@4oBv*~<0v)XN8UH_lHx*XL*7mfXh$I|KKNo$K?YceK$bdOcRI*W=}B<+cSKPws!dv{rQ+UA`c&o_4P5)1{4?r{|#E#{5>U=Wp9y-N(G5=6Pl1`n+o0LCtfjk?}rb=X(Cy-Oc;!y{}ri?oV>>KI->XEBD@4omxG7xiew6`TlI>dj5)W>bh23HT&Pnb^nL<Q=i-F@-Cx)tX%KMa{bkQIpUblJ1f`gDLp`aZfr-h{#LH*UveOIF1f>~zm@BLyFFO#>(!5$=Z}@^>%BRIeNo3eKdoHvmy2W6eH<EX{=8u2`g)J0s{GQY=JU(S^?CBi1ogR@iMs;#qn+#LSN>FWT^~<1>uKeBzvQN?dBQ(5>S^b?p0CYT_c3pfdEQ#Nem{TZVU>TMZ1#hd>-sF2t3J2o7PCLCTt6=sKc@1Hr;Ph$=ej=^%u~;W@4Fc1iJj~EJTqU-^GMYkqdr!y_j}qBweOnNDKOS=<+|S{E>-g^%-(JEo0aQ+OJ1SsHhsByf5{`s_4*T6^4xsDe4n>+z5X6+RQ``A&3?9WeZM-sp+5J?8)iRSxqg2p&$=11JFuVaT=#RuohrZZnRQ;7x$XxqPo7|$S9Y%Z;pf9@ol#rOpQp$ja$QgItVez@>uKe>o@b7!`xU>|tf!UhdLBNl_UViaV}IGX9-mvF=E+VppO03q&rkBK5zCE!wsXDTH-D|pr7N9{e)jTga^275Sx?@XWAw9?>waGOlgdLUnf+kp`h8>h&+5Jm2rCHeH#^t;HupOFXs_81R<74G=MOc{o0rXgBR{|SviZE2=6vp(=U@lp=NCKI^_&{w%ai^%V)mPr>wX(w%$MiY-DaMjR<6(6f-Y*Fk&l|^vz7aQKNjoD&(E7|_K%h8^_;j@UDv05%zm(PU7us!eR*V?n&$noa{avfu$Nlr3%{AqYb)3L{a_z8&$q|S^N`#j*Zse*uUcoNT<iCHX0GeAG9hR^?OfM?`Iw;fv~yig@<R2ra$QgILiMzAT~G2t^|W$5|I);u_4IPPo?dR()6R8$QZrR<{k(7IdcSyi+Nb9Gr<LpT+{-UKY@8={uFn%M9~qSsbbj(e^VfbeC+Pag_4+SeKjF)-=9}ZKTt6?q{8Qz1x)|%RbG@F^H&y=LBJ+B!Tt82b-&T3g3+8!f<$C_3At!w~@0oi2R<73{(_Q7Ser-NqtXz+;+fU`E$C%e^<^G>9hO2z!cJq3zTwm|CM3sM4&UnAFbAA3_nxOK~XU*S7S-D>S*4Zk*(rS+}-pX}9EPY1h#dn(hX61T4sV}R1a;==e>$P*;&q=SUyw?@q=XyUs+PVJwj_#XPe)KJK{Z_88xBV9GOO{zrE7$7}&!Y~djGxEtT-PUTugY_J?=k9Q<$C_&hgE)Ies19P+PVID`O*oM#}Cgn_oJEX^&Bra8Mse%zgfAi|Ncw9Jg;WWJfr?ruIs=47d20XBDqFAtz2L4>fhBoy~^ep^|W%m{+F)#^4J#h&GlHhUeEID>T_GQG54dD>;3rjE%mv7mdQ8fw{l&7^4NWM2OaO_di?ZKr+nY{o^4#Oo$KqJP|lZU)j4YZ{>RF7KPOaF^V}|#Z`9Mu3yo);g~og9_trDIlKR}xrF)G2v2uN04G&X!c!AjuR<7$`w~_kXiBt28{bJ?1e?p^GUb1+;F~5};8qakV8c(jrmuscgS-hdKf9+h4zu8{phZg4s*2m8E{yI89<)0igpQl!??^pg%U!J#YWS%j<mFxO%PEhl7dMzigKkZ!i=f*K=o{D$m8~4}B_4>)Zy4mCPzVODcO;(>fqo>gicCPE0IEQ(982w=9dVE5bn&)O|<2<x;-OqiVR`b;Q%j`ER*Zt|`R{z+!9^YoM`ds_@W##(33d>e?{<gJw9$LBXhZ`Hz=Qg-*j<@nc<L&)!<+?sswy6BiCgyo-<+^{4=BRZxzGjZMa(jHC^V7<G<KvBg{c|h)#?(a-jw34NggL3n0sr(zLizGM_&@!b)arlrPk&-sHvj+r)1Pr6j^lp3lZ+38li?wFA9x7d0dE0|*M>X5QFv823a*BPL-BHOC>(+pfkWWaj`GhP#p1c}X?P$0D!dQgjD%mpXTvYS58)%>hv3QhAb0}aA0Gtwhg&1zPDr>bJ`(N<kHcrfvsvFbB)k~Ug%`u`<DbLt!=EAHV$@7(R}2Z4!OOvA;L3PaxGMLuG7_$Zw}5NG_uzftd*IecI1V2Mi}#1);I8;UxGUVlRWE!HJ`f%RC*lckB0LG708fG+K*H1Taqu*FDiTh?li?KjK70r~g#B<I67Gga!QJ47cr~~od>0a~h=;-z;oFY#5LhH!fXm(}V2|vB3*bZeX7~`i0|~#5zXZPyufQLISHMr=lVNYqJc)$oxOxOn!6(2ea2(zrj)SA|)^Id@HxjOgcY^D|4UupMyer%R9)^#Dhry5Ii{ZuWx5tt27W^}K3;YQZE)k+!_F)MmTnaA(mxAxaE5nu9Z+9Z$2>c#60<MRIo8hhDW^fxk4vu5L33qbU(N#NFEnP*sYKymn+cBms67G(Kdm`b^cqh0s+yx2uLc%@pc5n~4D;^!<KOdr5b2GdN9t}rx4Z?Thb&zmlyd~TekHK5QF>oy27H-Qm3#Ymo;p%=@1Mq(M2v~e5+z;-H_lEnzt&ngdygA$mu8Bv&HQ_M43M^h04uebMcfh6LqWEz~aZ&hFB>Wz}2YwG;glEHx;Ia7MVet|0SU47shhyQ6NVpXe?&m5MPs8Kkc;-q&!hgg64*v~)5eaX?v*AtfUVIO{7e0j_hsC9Kr}$pjp`K-72QH6Sfy=|;NVq;83D<|)<IUmb^hbLnJQyDe4~CQQ5pWVb7Egu8!s$qOIuf3U-w#iO#{}$wF-SN*M4buo?3s9S@7xfM#rwhi*blKtI0kPO;@_LXP4Px>Q@Ab?u7THtYrvK8FgT3;Pzec_#EZfu;o`XLjpBSS{4XT@HvS&`HvAaA2wuc~cnk>-#be>2aC^KX+#YU#gzMt1;JR=fB-|432e*X#2JErENO-)fhw(@8RQOT&2|Nu>W4}FtgqPzl!pq^c_$GKQyd4Q2#P`An;dA&YSX}noIldRZg_nm#!WGEE;R<kdB-{Y64>y4C#oNR8!o%^w@L=}aa3nk)9}AC%r{L+Z?7NwKpXq9{t2D-^1<WZt3ZD#*f=44^?;TY*1<wrezuyYW`>(tw%RBKbB>W&g6`soY2a#|Fo(6ks&A_L?8So4|9Zu(ZXW+BoS$u|YANSr(bu|PD&vmuN)iziEM8dmV{p{)|S6|`h;jiE$Ncga;t*&;u+K(TG_rqV{=ix8lAMl^xAK*Wc@L%}P@L%vvBzyx2|A>DD{|JAHAA!Gw4{+TFxb_3&yYR#CVXkc#+DXmC*9Y)cz88ND&T=)y)nL3ge9_g1t}Y<q5AZkO58!p^4esAmcrFrt3;z&)3;r0t2!9NJ?dmuD-}puNB5V3L68^>2ulObW0(=Sn2>$^72!0b^2fqntp>@<|9oIGm?*mVPrFPw14RkdLzYm@SPs1O8r@=4aufQ+B8}S@?Bb<+)g!AFEuCCzU<0s+o;ct=fF+2x82EU8H0>29{#2<hc!lUu~;L&gwd?4HfZij@M;N9RRa5E&_!&M@lfOmttQQrh4JRhG1&xe=cFTl&-HTXt&4ZID{hqu88@U!p%_{)HM;O%8$+3Pp(KkzH?AMk(h@8SQzzvJJ+zr(*F;ji&y@YnFi_`8mOe+j>ZFLeC-QFtys+VSsS;URbz$A4A}x53-NZQv**9Dz51Bj8$iGq@I98wt0-d%!K=UXH&fdLiLtSF`X3@kIDRI1^8R#plDTU9EDp1pf!T1YY3kDOXRsdJbOzFJR1bNH_xt&%;;2^Wde9I*-NI<E!9RtZ6+Gmh*fKz6@XO`1^S^*Rz^+d;PzJYh1!wGtmNSvw-XIYV|a=oCQCNKLtMvKZAs4BH<bMbMSN2Lb$D~0j@gZ!{N^GD116R3Vt4c8Gasq2j30910Tgtz(?V4knne|F5_qL6Yv>058n;v!5i?G;SKOgd^)@mPREDC>F`8+04#nlJQ2R%)fl`xelOe|Zi<8(;{)IU)V(nhu7QN>BjFglGaLgC#z(<};Vk@l$N$_EeiMJk@jqLIKf;eX{%5i9CHx!5|Lhk26$xL(zk{#B*8=Y4H6(o9QSWTxKj4=g|9hSA7x)>+{~jp3AJ23A?~TG+@eS}+_%(bb{2IIzPluPn^YDrAMDDA1J_u(x{(JA8C&IFiX5vZs7&r;;iFb#4!p-rfaC0~k3D?9M!{RmIMy~F0b(f>gdGR**J&ylbAnZLag!>@j-gqOpH|+J5a15VWh0l$|!|^I`I9$z9&kk{Uo<!hP@oI22##cqcVR#K#ygnQTSI1-E7}i-GzYDGoR}QFAWjq3o;Ik{^VQ?{5Wn2|S!X=P!X(U_@30FYE6_IcyBwQW|mqo%Qk#KRm7+f5_0||Ry!XbE3NB?@v$3^fGa1po^UK%b1hvMbnQ20)~0$hP>6ONAyxg)H||Mb6d@PB2=qKyBsgZ(GXzXlHclegTt^j`|c#}$)$xP`dG_riOmt9<ughSUPM'

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
