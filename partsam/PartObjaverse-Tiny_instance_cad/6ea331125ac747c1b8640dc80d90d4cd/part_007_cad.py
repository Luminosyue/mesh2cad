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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/6ea331125ac747c1b8640dc80d90d4cd/part_007.stl', 'relative_path': '6ea331125ac747c1b8640dc80d90d4cd/part_007.stl', 'source_sha256': '513f2802d092bd531836e022de0f22087b9258371708a4cf5b9e3051990b4a14', 'input_faces': 800, 'input_vertices': 451, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.04865650087594986, -0.43026286363601685, 0.004430428147315979], [0.1763608157634735, 0.13971170783042908, 0.15680935978889465]]}
GEOMETRY_BASE85 = 'c$}r22XqzH+WsffK@c#A2x6!Kr8h%ADotvr(g`I<?=6&gfY5shM(QDiBoqPZQjZ7-HoSlr!E$3kMHH2yaz*`SpZ(jDnK${b^<UqYyPoy@eD3Bwv&)>>v&ka5O^%%5mi{SY6<*(J-npkOOX*=N+?o_SZo<%kvE!?a8WR_06%OU<$M~xDUE4+X2(u<x(;^4OjvqKKvOz>-qrp*;RU#q>j~+K+T>nx1Mvog5tMV58M~siP^YKIakBPPayHcIHHLFC_u3RNzM#TT}C%=6OzL_`Do7x`CHQ_Dg5hF6*ZtBW?pG^+sF$2$g^5F2Pq1>0e&zt`|CzJ<Xx#i8PEZ6m4-|nq{?Nyzxdf?4{8};X&zu?VNQ$o4_pJZ?S&O1Z7wegNOUw%;6fAkG+9)3#K`Q@g!e#+@k9{ldIH=lM+_p9Q`Q0_00V_PUMIY5uY<+I*=`yhS&3$J_gO(R2j#*^vZ+>CSCe>{0Ge!l+P+H1V++a&5bbqk*M<aN_@-g~9DPOAgDPVv0n_NKp;HhJ4;e5m_X^*3++@fBSsc-VVAvDb8d;*(Gw@nr|yeq>LbFFxbReT)0)yu|n3{QOXTJxjNG>##m!=I1)?X`h~;>wK`xTPMeAef?dEdfErC9MbbXqmZ}GKbQ3S$@yPzox7ju_B9WBuczo&dR^td7Rm#~u4UU_lgs`(x#+J`NA%ZeFZ%1`qQ6cZ(O;*%=&zHD{yKF;e`7AEZqKg2CYSwna?xL>j_9w`Ui8<=MSq<-qQ6di(O)MQ{dMZd`8`r`XSVZ8o@IVbF6Y<Ok@IWX%lS3AoL^H%&aY`N=hx(NeoY<GU#n7ZS9bk1x$Li#i~c%wM1P(3qQ6cq`s>sY{dL-l{yMqnuTw|%_xi7Uvh6Q<mj0St_Se*r{Wa}ne@!m?YwF1Un)W=8V)C!`){*02aybsBzFg-AX79~*os(x-=O&ly+|-fl+_abL+~jhdn>uoxoAzQHoLsJdlgssQ>dSFx_ujs2$ALV{IG9|HgQ+9O!L*m-U~)MQrj8s3(_W5)$>lhhT#kdOFYk+Qr|r-7z97$XUzl9p7p9K9FHC!RUzl9p7p9K9FHC!RUzl9p7bchYg{d#cA?aH7<3OHe98509!PJrCVA{)ZFu5EDQ%8=2X)pV0a@k)~N3Q>Vkq5F}|KwTLzscqLH+AItH|^#6H@RH@rjA_yroCL}CYS5n)Dis+mhPk5i~YQli~YQli~YQli~YRG<$m62FZT0JF81?I9kHKx+Kc_X(_ZZ7om}kaojPJapAk30Gmqvy(d6<y(P=N<6P;YVCpx)!Pju>w_e3Wb?}<(>-V>er;yuyH#e1TYi}ysQzIab`a`~QEa_XC*|37`{wUg>|-#?Y;&ST!Iqw_pb%iMY3aw(nP?zGOG`!2qHHI)Aux!RLg*dEG#`-TPFc`&wrDEH5~^jhdT=FQNbJLHP4zw7jRcb@U*gi!7;8MWD+2S3lL^WyPaLiOt}3guRgGM|R(Y<?ukoyW}mUe{kca)mpO=(k+giG5?fJNIw;UiWK%&bglYqtioq@Z?ilJ#}7**X>(|FLCF=meG0~+9oD@@&eU#`=p0gyK`Ua<2qkCe`Bb>TbJtV*-#+VFW(2vH@kDI!x4S`dGe&V^FY3iq1^Z5yP@k0#3$;{z1dW^_qR`Q=l&A;^}P7YgyzM%nWWn<s~-AX|Dc2o?%aR;zP`@5sMOHs9yz41e_ath{$E^Q>dyUn4(iWcS9y**kC^+O{@en?XL{Q2?x*V)E;!$vTZJm=@!!01i|2E17uM}hpIqV2gMZ!rBs31;RYU7ACi19W4-Go#em#A3gD2n7LSKJ@CTrYz#=%Ouec|!R?mTe+D(kkxR(Ec-8mar+?blRy?yKEQ=jR&xJ?$sm)9WOyQJSaz=Gi*m8|JAKTy-PVFDviop>^&%`-dL4LId>mH~nUVJC8a4lD__on~Cl`BQip_zdUn^r_P!ax?fGp%=Xl|(Ol<k{+i~_1K-@%^U~^4nkR4aj-HoGFU5Q6KRZ?D@6Jwj=Mnom>-7-VaIQP|%`BnEA?4;4&-LuKbe*!5SGe<F&M)=&RPGk=T+iAoI={0oG;V=f4|HBSO5b1e4<);E>xt{3{stQy-|Ei&!^Y|SshOev24m|T34KnvDtbKcjb7}|BPz7f{VH@U!JTK!DX7QoZoSa`8*#C|uCs28p0DJ8Hn{VMZi99H#DPS29@F})o|n;cXS(y?)K)t0UT%sz_gDK>kLRwI>7M$(pVH%*x__#tPT%qR`e*!*>drGhxueJP>(`fi>U6%O^TlHWp7sUL>wI~V{(f%KSoil{vrxZ+k@u3_xs`BBU;krIrh4+dll1r7oO_}159FMn$6?Y~J^o$d6WzIQZylXaiCg5(BU-($>sRUFcjv*bFY3HmuZf;KHh9%No+h{YkJRJyVO`Jl_}Vtp`MXPJyYr0Sa_aFvIx@vmf7B0pe2(;5?#XMN)A`Sf1Mb{k^tjHe&IpaCHFk0+4;-DQ*GaCD8{N72-t#poy~Ukp^uDLRmj(|>^|XH>PUox>ll!Lptk><HKq&X$-lFpkQ}j6hIv~-VTYDPl>zV({LU-=pe?gCP#Ru`8_BC7UyzQv*p7xiI>+$bXZ<0F?+#Ra(#1U!kJXpD@&Wl}`<<2AS|E-@3zb{MieD0dB^>{vCe7QT%h!5&~^V)!?e*J@?+&^t}X#6w!rs?Y(JzI~%p-LOwxfRt_kN*_k7Iz+#a$k>gm!woro%>VuIJBRW?#?4N+|uhO`U^e&XD1vD)hX3Pk8{6`3*EUtsgYiXbNkP7=fTB)>g%7G5*i1q_LNX=9h#@>45_!#od?%U*Ll;fiJpAezw~wHFB9*n^KcuT59>Y7otx{o7F*lgx&Qt#oyV7-=+0vXzO4KE$GkLm9;lq5=jFuj%RF_sFM@HK1Mb{+`wiXx-TtBZirF+xw|}LFo|mWFZ*k{=x)1cc9NL%a&V#$B>+k;sX?pzUCLIsWPuqAs?@L=Ix^w^UdS0vtvlhDZVDpQ5eB$@baOcjrrBoQ_&V8jBpTj>*@Z|Fc>-%wAVwyXTIo?pud$|^~JlFH@`+EKN+>zpGKmH3nKD|C$=BeNNs2<Nw=>gAmHrnGE&y3sabo-GDJnP5gfu23}IOOQM#hnKW|E0grmmf*><cza_z^-(6Zk_r`_jgbp{r3dd4xh|!{hM5_Pm{~_=H%jjaq5Ws#pH4wI(5W44750QGQ0cB<nsP9xm=$nm+RB1Bi5($xn^C}ST)X_%lpyf^1d^<ypQ}#S_DHbzV}R?<+(sEzYm>UJ}=1S_oVZ=@;PF1@%`!4H_w+xw~lw`S-w|I9r@fL&+^<M&+^<c_2qNNT#tP2n7rp(-sg^~FP=NTgueQE#B<-|a$n@+Vn1MVxnDB5+$We^?xURgV*g-rxxaEgSL`dC_F~^<a=Gtv>WF=pbNyo9<<uAZE+-fJE@zy7^6tC*8>Z=T5c_kJ`&vEYc`q=z+_#%t?%SREVt?+m7yEOky?F01xqR<%a<QLx>WKZk(_ZZ7gPmvS{)+b(Cl~vClgoX+lZ$=6$>sZtzubDAi}zoX%lBWC%lBWWj(God>WKGWlbiQnYs~v;o?N{DI`zf-ugQJOx_I7yom{;CI&~I?dES3b9{i8@{nxo3`Tl!#gU;pqFL{>tUvl~W8*%3d^X@(WF}XbdaoUUX5R=PuA*YTw7c#j#7jo*0b0L$<b0H@e=PEJVj(NT(o%14c-$%{8=SAe^yeRnWh-7ze&Wn5>x7zB?vz!;1T%HS=I^tX?qR9LD`o;O4$>sT;@0|~Hd(QXl`)q?d&vL$Z<D$MEalUHuEa#Kt^4!&_BhM|#o%7gp@6UJV@;uY|TysuaJYue=KIgR7caMA8%X3<j%X3;M7w5Dlm*=#BQ&)9=#re6(gT4XYbMGmi>h|*7o7_rR<~g4?d6x5Va(O;)a(PZ}a(Qm=<l@{u=1};l?5;CrdC61Rtp}6Kc@O-UrrV2sS4Q%-P%igxPA>LcCeO0J%3E6heUaGbn_TXDO)mHUPA>NUG37g*_SE6MEO4!}{`)TR9%pj-zGiayUgqTD{VVv}yffML%jEL?+T^ldCYSFiCYSs9jGYV4WIGPMADr>bqdA```uCaa=F!RJ{+V3PWALw)XR}++CYS5h<etA*iuU{#Z0mgEmsu6nC0SNJE8H5~-}Ni7q5s3O9MAq&V29TE|N0f!s2Vl?ufGDjE6lR?*?Pm)A^b4D4?YYZMT+<1yW#!t9;A3DQoIA-1@C~j+1if3j_-nZaUHKC#d}@Xx)&)vh!h`3ijU!k;bZU#{3v_^K55II4(labgOK6@cvpA;JOU~1Z0kAv1-vW#0^A&b32qLz#CyOk;TQ2<@QZL8yf@qiZfmPG-V^T)_k?4S;+OGW@XPREya(Kau^5aLPeF<&;RE1F@C1AWJOLhu6c5Kc!^7c@t}*S1H-$UG9q`6*2e=*H1a1en$9-^nI2wN*j)pto&EQUO7rX`B1@4Bog1f=p@z!u_=A%1OJP?nC2f`DP;>q~S@MJg+9}Ev>ZsL&QIkuMK3HTIv3Uii#6wksZz_Z}R_&9hmya*|tjt_^Y!^7~7a7X5B7*aeGZwC*Bhv4nuA#fi&8tw!4#XG@$;eL1*xE~yYcY|Z#{&;t|J9E<?DISkcgvY~vq<AJi8J-Ex#^c~P=4Lihyv{X$>yYC0cmkZjJgrBH*W!!ewQv%?2u^~RBgG5x>F`2$8a@mj#ym|!il^d3;HmIPybnAQ9)<UXN5P}<e(-2`3?2iIfyd(g;r`6WSfuzB+z-D3FF}f5#b?5=!mr`8;n~c`Ye?}%d_BCLao>m(Z^e_~t?(9nIlKj4gD-^Fzzgtc@HEDH0a8349|_Ng=i;N_W%xXN6g-M?pNACBz{kKd;COs2JeKi|M~V~iCGZl)HxVh`fWHQBfK%{|@J7Zi1u0I(x4_BpW_%628D5PqfEO@EtC8ZB_*~eG*Gi;#1wId+$GEIOidW(Ba6Elpg>QgY!2vu4PN6>md@~$?H{q+{)m+~ud<DFM&rp2F-i!Wf>kFj#I{piM9sU|A{@K>w_&@kB@ISB>ru|n~NpTo{2M*&pa^Ux1CB?b$-(e-id2G)eru{emTjjqY#or^vH}HG#4fs3!4t$5P_zo$)f)sy@Uxz=2FX3Oqm*9UP#b4n+!(YL-Tw{6*{|mka|Agla)BF?s2c8dBQhXoJ4=XADFJ1svQv4_WFs!8b0sauIr1&<T6IN1u7tamnW`6D>#s9&-hyMfr8!7$-zX5*&U&X(JzhiE$BE|39I)b0VufSKBvr|ZM5WfTm;gk5k;FIuqr1&HJEBGV$bNm*3i#huoDgF}w1O5`u!0*Eu@DKQZ;UD0e_@D4i_(%K!{3HAgejEM<{uaLr-(_yTMT#%u|AsHa?;*u+;h(^7!EfVN;j7He+eq;N*ZdtoiudEE;8V=gex!IWeiGgb@4?T*d*C;b;uH8s@Co<={yF?P^K=0z{t(ZAKZHNPe}F%Lui-c0Yw)M|kMO7PXZSbpXYfV*Tlib%<04Z0F8&_;E_@6regl6CegoczzYV|5eC$Jtx8eKY{fzrIq&N-V1E;}T@i*bE@NWDByc<4_Uw|(#*2j_JGx!Ja8Td4Q4L*vW#jnBF827VC@jLiu@H_B1{33jj@jZtWAI6Wt#~9zkNbyd5AG{Mz$G5@T7`t?&I2GRtr@|@tZa4+rg&&8HGe*0R;@9!huo<t{k>Z2+S@<mDau6v#gr9@Y(dR?>PWTYK15bz3>CX;41>ON~$9KWIxW4W9LHHn_p}3U&JbK1fI8s~%kAkbf4Qw^U&H0St=6F<C=6Q}{b>8zF{wy8^NAVfYBE?VRrQoOGlBg8V@BDB9JRB|no9DCg$MA4Coc=t96qm&tz^0#y3)(7es|fxiTm&wRSAq+}PawsWZPml;;FaJya9#XKxGr23FAZ0Pt0Bct;RWHR;G#&e*^4Uv8!rMYDgFyD3@a(lOZEhu7dHE;e9TWi@{)LE*W6WRKFwH|`K{+#1B#zRiksqf;HGe6ye`}rZh}{Zo4`K28tjABnN~4dWo$i)6i3*qk5|Xbz}4XzNO3v57+el6gcO@Syy7tY(Xh-tzhaAdvY0oEyeJ;wn$rm8*<7oc_xi52QJ+3O4>!ZB!_D9pcn!D(tj_8lu~pvI<F-oR74h=0@|ti(xOSL6cU9g7uNjtkPODg*<F>>b;x*x#)NP0qm&G4}%fjYfR{RiBoD+W>&I#vs^(Qw{oQFBe<(fOi#qm6F9@-a2iX-uga7FqYi4-?-jZ34j%ya5SNO3K^72JxssD+n<Yrz%pLU19jsRAAeNAejJ__G!G?;Sh`)bl{SJFE9#^*;Qjtpm1>*h;gNYAfB=TeeQw3ffv{|CtT8UPFqLkm6U7;<ZTedZc(0QoI={PDYBiAjJWscq6_J-Uu(lUxSyyOOWD4coLk%wJt)67bC?>@wM<;`mhu!UXB#6#5cj4=-W!9cr{YI22X~Q>GK+-I1wpcg$LjO{a=L?ufUhV`E2F3)IUq3rMLi6oF6I9ixlTVigO^v=0|ZDQv487oD(U|gXe?uz{T)~;bL%cr1){X09=4;eH<x%3@HxB^TK)QLpV}g6e%u@=YVt2x57yM6hi8!ARY#X(dU9l@gqoa5j-cHll~V$iXX*`!QE{2xAhWIJOCd74}eGFli`u@6kD_KnfPRQCOjJ{j>AX5aquX-KRgN^h<Aer!rk#UaCf*J{v6y6egS_LegUqJSB2}t)$ww0b-049l6VQc99#l^0x2$!SB1;N)$nKGYH$?(92^BdkGFxJhuh-a;BL%iTco%>QrrU{0QZ0g;UnQe@MwGrJQ|+rn)|6pae}44uaqywXIYuwb&40^Gp)?;L&Zz**;eLvsbcdTt9T9`2hV}0;iKSb@ECj`JO+-%yTh??PrM!66YhY&0C#|!<MrX@a6`O0+z_sbSAc86kyhr~ibRT^wDkR}{1LpQm3i+gE{K<~GQS@b7s8*gGQV3Co9`UOrSS4_DYznD4Xy~+z@y+Aa0C2#xB=V@Zwo7L4@cYTWve4n+#4SZ_l94_$HFhe<M8S5ICus=7oGvnv-I;(`Eq=&mHBK{Y@WG_6Y%M90z4HTYh|u~#iQ}TR_6Vpco5#p%Dlf6_rRmA%=<B#F;d>b%DjJDFmB2l!Oh?XcrDlX*J6H@S8~l)CFWCkY1jOgX8sG~Me)*B=Ce$(dB!Pz3a<n|1y{yv!Ik0Kcq6zr+!${GH-=l{(XjH4aEz_tw)!E(!|+M)FnA*FhbO|X*jj)u#QpF>cs^1bk57W*;R*O~cmg~WkAa86eetevU$`^g8tx3Y!hLWnxCvelZUWcAtH5<&^{)a(;AQbDa9OwvQv3{F4}J!&i~HcZa8tZB+!THh?+U*Ncfn&|<^A9;a3`d=4?Ya;0}sI`!b9NkwxZjFJrthf|MgEOX8x$ZhqgTbprZVf-d{U&|H<6;z&O8z7TqRSX#e_<{Xg|(@SIw)*8c!sh1E&'

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
