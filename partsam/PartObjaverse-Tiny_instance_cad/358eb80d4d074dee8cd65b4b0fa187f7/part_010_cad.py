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

PART_NAME = 'part_010'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/358eb80d4d074dee8cd65b4b0fa187f7/part_010.stl', 'relative_path': '358eb80d4d074dee8cd65b4b0fa187f7/part_010.stl', 'source_sha256': '2548766459ae226c1274e348fef71fb603feb17695be8f2628cad22b2c216798', 'input_faces': 654, 'input_vertices': 436, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3243614733219147, -0.3258565366268158, -0.4846172034740448], [0.3243476450443268, 0.4023354947566986, 0.35070452094078064]]}
GEOMETRY_BASE85 = 'c$}r22ecGbwuY+}1QY}uL{yX(kesu`MiC`R5EPKmL`4zs5*!4_RzWfdf=CdWoFqt45ahOmLCHZ>kkE!fM;%8Q6C?9@Cw!-@+PB|YZ@uTNz5d_t?6Xg(>bh0k<+N*cb*>_w{pSuZyYXjB;^jS0M}Dt}H=<wGumOGg4XrY0$jFFS$Z-9S(^nqo)TUjRh&RF;Rkm-xp?$K-){mBL*uP%cO3||Y2WJh->NTk6;H<v=G;iK(;Lv`G4}GlHkbdgl%hjq`r&6?L`AX4eqyNW$u2oY=KD6t@Y(1rur;SE;Uj8&Y$Un3^{`TW1nkY@Q8W_q?99VNUJIKlR_TGF_=f~G>I$_$E-fwxu9VfE`JiP?oqT_y@AFJ^AiD3QocWcjO2RZel7jFGX=cg{k4NoN=wBr{!a3(v*pR+t&;I0pKzSm&uanrwL%<|RS&HR1d!t&_S@@D?2;@gjf=JV^-=d**{?az--nfavi-+U}sKVGY#nZM7epQ`+<sh^${-*47;#}zYQZ*J1;kK>7`<%u%4nf*zgXlb}NsJ7kzO<T=+eg357-r6!|y~zRHcbocc>X`M#rc5;Ic>K%ScHIr{JQC!o{_mLiCO;}2;>nVhC(hbBv3m1UhEMHf_owrLRFe$cYy8db5MS8leN#u~!;_6{e)>$OaGf31_k{Ruvuyr$c-BpZ#}{wj8>}z6tM7fYFx&9x<-Nf=skLJ)f5@KKiTJm>GjTT`$D`+#nE6CSzT>Wb?Bw*FW}j2d{u<1e+~p^|LhqV!JCxZIT$ki-U8(B%43F(AcGMh~uBS8d<j;logm}U9Av3<rhbPF7ANq8MS%1UhM}qYwPs;q>O%4a^OYZ7N=dLh3e*V7D{3TC{{Mh;DL-Uv1)lav0(eTvTfqO#xe5r?>&yP2n`qA1~XXNoILqj~(D!<{LHz&jsOHLliRL5~y$MMwH+d@3P<u0>7o~Yw^Ow@5aDe8D%{%ZCiedV<fkInh=P^S8hyZX^0MeKST<+bz7o5;u$E#I)`Ro;u+%{)&3v?uhr5Zvv5;+E9*O!Xyq^}X7|w`V$DlDmC&TplmS<?)hS){)1{ae2HXkBK_+c=_`e$IEefyd-z^6J?8S&-6Kx+<lH5m!Bia{m<!7U%V6iy!)S1!ILsyTn8j~^}U0~3{U2sYX5HSIJi3#PprKwlpn9S;aH}8$7OzOXf6BqR^&S#7x{_LMw;t+T;w|*BR@6mEn7!khXwbq!;Z`Au;6ZgQY|;zahq+~VA?CLeJ>M_7djZuf2;Ne{qN}tA|LLN@69Y5s*`@=hP^@VU1`7GoF9&-R&O);8y?*ftS`B%AN{$z;py|0KQ{cttb^GB9{&Q~XX=q4Pri5N6T=sT^OK{`8lEm-^JDpLH{AR8>CM4;#x~w+$6b2S-iM9rZLUL($G@>W^+CH2f;@d-k(p0yR+z^dFE%_?!`AV}dv?7g&e?sdamenc<Zj>K-sPfpKSjRJ$xqZcztxP}sNr!lpWmC>>!RcHEl>V@!R${Qo@{;LsF~-uyN?8Ue2wMN7rrw2>HSA-{&Q0;pRjgckf&Ezp4u~FPmo7j^fu#qx2y~0$9q{GyD;4D&*e>)Hy>r5D^iQ>{ioy6^OncI{_Q}Jr!TcO_qFlyWkUJM8Eq^-a>?e;8)ozGNE@CWc*4vlH5a}kVV`Gq91rpMQOnaC59|r?+O|%t&p|u?IrR<q)*ZI@G0Vmr4)Pd0-L&D}AdjETK4tc2c{tzk#N9SOzP^C1zpcgQ;Q5e)yYr`2`fbCfEHd}$?*346cYhdb+urc_*I!xg?w=3Uw0zL0(BEsx{rlvq72Xc+L;6&H`}Yv;_90PV^PV90*Lymg@9)p`Hb1%K!dr$P+Znq4OYW}cjwgFQcPvxB<1#-{d3NafFL_+#$I9Lmy8cV<U;h{Fw(}g<(mWr=x7W3Q_XPJUPuLscZhvIH+aL11)iVrF4H_N(`zW~o_YNN0_1>{e`Hsu{#Jz>Xe;);pi~Qtw^TK~01^4%->&u~iNcU*ZeL<KfCJf#i;%*;$ihQ?k<fltaHQZ}IW~-^s-y_N0-=p+(V=a&8>1OwNM@F9B_pdPTde6*^`EZw?{H}}TNB3m~^Ci!bf2RHPjQMbv9~)N6@>HP*&F7bV$-VbQ{>4VKgY_kM^}W(pwwU8S_t&@0K6Cv^oj7f{mpt3U{QH+*?8(FvJv)W-hcxYL#ykE@n5VmDWvm0wQ3oD>ZEl!X7%@F#9e9p9@EmpC8uLoVd0ty$X2$w(S3my!G|PXx@g=j5pZ3bg)5WLS>-iT?T0ZvgZ<#voen4`!|35XzSYL8iKUVO^&6$pu<Zk{x7st!z;&@4(qmDRUJ{QMJ@*H)<@$$JiUOpGcOLA8~+5FYbnLbC7yU&r&#pg(J_c@9m?zuVmd3X7e=g1e=0m)r{^xL+UZ~b7g*7VeM8F{SxEqg=!^PRIZ=EHO3mpHo8?5E6!M`ivGJI#G;Qs%=w^1b!7EEm^d$^Gk+<Kj9jxu3uN>rI-=`)8kv`{(pKmdpER$L0NVv|4eSFQ04RIi71Am(Mk>j(Dy~{^Qg}Gro9!aa=yX`1#`b#m^VdFUfPIEEo5IlKc083-cK6o)=;~FE}or7aVub3sIgI9GA}v@$T1HF78(o%SXOxj+?memE6DYy|bI)iRjDQ%zU^XkUU+`-VekE9Wl>oiP90n{p;<#L-x5^Jij<DpI;nLisu)fi|3c<Ki)Ll>v6{Zo#pzUgEOCG{i*hOlINNf&oz#_=NfO5eXjBI#q*KlQJ!}aJntlT^|j+J>bTVO<MS)IyFU25^v0PP^Wi!2vs<h%^OyPXsK`$&Uu?dwNQ!*N{p-mGg>0QkO+(j1$zw9V-6yYQ%!lX5KiO?naQ>1<W&T|?Lf1pd-Tb5X9awFSgZLg*a{u>*y(?Fl^Gkle{qVGv=6sO9BM9z)UY=^QBGY-8gS+R@!MRps`n<#=-!9Aaxs%*|?h@-J87_Yxk=%c7{m-%`X8z*$8p-|NkKpq68p&OKZ|q=ONBmCYUG8AcoA~zw?DO4Y_PXtO^rGdl-=-W1^7x5j=6W9A9p=%r<>|$*nmVy5?QOpJJxg+TyrRv&U1a{fmS^guR`s&y3p_f}^28(UKM3)2>&<ghY)|h{e!SEM!;{z8{KVjHw!Zj1&gbIyxa6#wmW%IiCHJ4l;qv=i$z{I${#Nq1$d}*WO75Od(@!@}2G{F;-;~__zUg!E`=;dn?~m6_n`ipV`+UjW_kMX=&M|ex^H;Rk_2&LeKIcmAf3N$?L390;&)t%{=V+gc=WfaU=k!xoUJ2ImzxNQ_|K7uK`MrnWe*WTqGtBt%dnb5~@15W|zIPJbeedL*E;!w&`2H;ich|Sy?wcH(kNZB*aru3q<MR7J$=&yX-u|Yx&dL1de2c9adpyXKi!D!FIbz>4_<sCE^Y7yO=N#OfKXCc|a}MsV^HYyaFm=urv!CChL+yOv-UF7WzWUtEC-%4bmW%J<;|Cj!GwT)CPsio;)6W;zPd{H=KfQ|!#+v;R*F(qU_0Z?ydg!>k9;T|)HC+DQA-Vh9#izA<-f;1IisLzcPidE(FkC#xN$%f=I4+*!B+rpAp5r8s%6#!0C%L<CNxyk=WN^Li_bJKU?^8Y(zfVc-U&mH<8kF%ogv;~LYZvL4@pA;1pCdK1OO3sp@6R|c-=A?@zCYu*e19f2vHDW8kDtbD{j6(`26<{mpJPED`?OOiKVEdzksx>Zjwi0kWv}}mRkiiAJ0A`5MET*zf;?5FXei(Nq-2P@e8;2PI~ks=mu2$PSzSXs{nr}Dg4`?jcql(LsdR|De8-br8tw?LH*wXF5O?c!+}qbKoPTTm5cl)p>7FgkdsXs%DxZt@siMW=_B}Q6zLw+ieXaEIV#iEB`97HA@_n$+-!WXiZ{~CHzL^)<dOTR)f1k~9@jhERJ8qv3#rtwT7w^l(ei(2fG#~dqp5x+uym*Vv_IEY;z8_q^@0Tn*@WWtz_dcP|#ruTG;=4lm{`-oK2j5q07kWE$L7%QY%9T)Onu>g05wCx*z^j=Wn$r-?{A%WaTK}t8Gwal@_5Xb}^U;XsJ*Hxiit#EYs(2E86hA@5B-$s@Hl99@(f$~16X-K2kTU^)lUnaIrA5%m_@XMN(ynzH{zes3BDP)YRJ?9;{fdz1awd~EnL64pQ*A3$yoqkYFIBPJv+c`i(|&`BjkIs1P5Vx&*259ou5}~1>hO7wL~Q#b<Y?bjMYo7;??#*U52@%(duQ6Tf0McCcCDSs?MF@Be=c+C$@rT0q`hC{4?dT9Yn_H)j$eVkj9-D@gwDfn!gr>&9=|`@4c{LhM?2%S>b`O2{2F6wor2dj`!Hv%-SKl6cPjcaUf1fum|FYdr&04|bSl0lHTC#fUt>S|)3+bm2d~GP!#G-du$HDOny84Ojqy*b7*6|e+O!{`Vi@hiXnUGIjcIR8+X(u^0y!fBeH+uiG4-{tui`Eh4bXb{EEP}D{uFK64^=UQ_93)o(Wf5m^=KPPp9X=Pp@F{j=wFZe+7DHG^^}S%bO`>kihp~y{ok}{|GSDyv|pm_GJS^7K7_X4>5~=6`908g2>pjpU;C$3j8O4sbU6NsivObhzi89mQ)~DS?f;?e3VnvtKAbk~pAOXfGtBiJPXFQ5*M5SEi7F<elkhjHet(MCcC8c1EvkHxh;1)Ij`ox3tJ}5ewxaZR^(NEq`c9(uB*xZ$oYJwLe&xsNOZbAStpM#>b({8ul)pY=+pi}_`|<SE?OJtPA^N*|<7sz&U!wL)jII5%N}p5l7c_zYS;eoOZU2=v?SE168|}Z*_A`AFv?pl$g+6}?<opuoo1lM!`r5y!;&~Ng&=>Hz)m*QR*mkYYlY5Qwxgxeb7dhIGp|5V&s@txizpFQfcGvd>YQMnP+Ux&*;u;ls(W~&QRoey?E73Rbc~skVx-Xg!ze=^ORj~$r6Mwy@|1%OhPJYJFew}LD7_sAQWDM;K=ws{IaSAeq_RCb;iijO&1!HKRmpSJ`J$x>FZsw=w89{U7bCaX}O4hg(U5;Oh*Xz)#*P#6x*0>(sgkO(ehi=5{wG?0-TJ;*V|C92Ilom#p;B{zU2wjZVq5TbL60al4Jg>*Q`6oGcEAgw*#rW0ub;M%Uv6%U|buHnTYF&h1g)T!E;TN&CWr1}TB>u#4y$+ubEsW2H&rKBOcot^;?)VnsTrI@<^Ab03j@`gsXx~#s4;9_fZg|ZX!g}Brplk38@T*lck667AU4y?@MYD+YTAN4y;Hx~#n&DS^R$s@j#Ls75^O@Uxcz4FoW8F*5HPl$cTvrhb1ASg+eXql{@1vr(ie6|OulW*KZ~S6(J$^BMor;zbtF6%W_!cVek65p@W#kXO*0bz>{2QLtMff-HN#>PgZb^7A#?WK6pyqmNtY@xki6wzPi&)<xxc1dm)KF0#t$^>Z;vp3e6OY0ws;H`>8c_+>S4C$PU5I|L%G9esRDo4Rs}R*-T^Z+5;t^O^d}p)^z9!>WB5J{E;vYgE#`k4z9nntsj`-?m4SX%?x_zj`yectgH_vL!s}pr=5dBzpKj!TAp$qHoLcc0#HT>NwnyY9{)Q8=J)+ZXk?n4_8ZD7sOHbiS!9ToShsEfA1*TvUETjE>NzaH8EU!R(Hp{?-s$f=9g57e*E`1Q%HL(P`dXvx^E(fjfDQ@=HP&`3pFqIqC{8q?M&!1Nxpqpfj(HK%_&!m*f&rYbrR+CQkGJ=z3qif>H+CTM&71JrMbHo`ZdubWTPKwBfmZv>A~r$b<_Z5g9I{z0?@{!SHTRFqOt($im=cwT9=6uuNW+BZ{iFa7R?YhPAfTgs`3L@d{Nv(Z=av+-9&tm@pW=u-|~T}6$EtycrCeN7d$RMdv+ygF!Yd~I^-pm*bov$osN()io(QM3#`im#2{i?5BJh0ey$!sm%t)$7PZXkQ*JhcAz>i`Kx`#ovS0!Pj9e_plZ{@0$tjZzZ%ZfkyEq@a53j_;UD}=q!92HAY*;yBmKG(Uv)CZ4{VuBi5v~VqlFG*#oWl@LFfGS2Gzm59dQO&WUE6Q`+Cj`KNs;&P(mJ*5urYaDJ2xoGaDQ+W4E<qhf^iw-DOjj+VgRjxURr!<WUsg3iRhg3qhQYOUgdh~3LJ__o9Y?331p_(u4OXa#&ld_FWUJ}-Nx{dY>gRq+k_cf97eL@fIje{;lYN&L<DJ5>AyeGV;&e^$k4{AltVkHSXdOQ6N@CGa;z?7XyogBHU-$5_u2C8<%8xkiaw0)2|H?qYE5e^BvH72l)(z-xYc#Ik?lZ;MzhgTD=br-~QQ7tu2K=T#)|3Gy5-4NKrlp~dl~@V7?nytICg7RSHHSkDt>s8NQwmL_fw^wIhQdOQ9t6+2aA6K})*rQ!<}UlKpTwyM~n;$31J>_-)UQ*nW~2z!TmZxh>LJJ9XKyRfeq=O^N8*jM<!p%?He#@|M~2TS3<K)=L)#=I^PpTj=G??kil?@`z7!#3u%jXAq{zRSEmr>@)2i>&)1b9Vc1fpuS?-*)s}{1Fu=RGcFA!H%N)i1%S1qVE%@VJFbj#3|Tr6(?2fK|jLp!S6*s#(zxzz3BV+eboFb`U!q7IeXB3f%^Lxe;>KKsrfNAK4$Dw=t=xZ>Yri{_NzEUoCxgC0owKlnBIf4v>gbr6ZAhzICe<IVHM{I?b9mGp$E~!_yhDmh@QiLO8pPe{rH3Qb@MqKXxq>D`{9SEb3QQFGmLQ#pGME)r>mHuVw8$!RE$(H8XbinMUM8zR2-+@ak%#F)ODi0ib@g7b>0mTtA!)h>(IV3S_xl?zS{Rv(K}-6^@eLdK*i%Ko`CDTf#?(XC&(FyK7${~+MYy5<DbM2LucTJ;di0O@w@Q(S)*Q0enR^yXk~mAd<V2Wz5{+R+8aL@KMEa)AIMrpu@*h=0fhEX5ZVt$hv5g~x1hW5TkzLKtm-vrKUT#!#(M@oiWtWnwT=wTc_eGn+A*-kj_iTfYWQl5Qw7bBFU+}837w9g&iSYPD9%gmwGQCisl@rwE^w~&LZ5J+J$j7L{&7P4LFi!oApB-@3w|^H+K5%XhHDA!tEw2I;wAQSEPfpE68og}&-jt}j_8B<j`(V5ReV*((tf6jmsQL{r{ia$b5y*pVxfxp=mPxfv@ayIpNG!E&%@7F@d`Q}orTxq&cM$g&+(bC8TePx*YL06=jvnEDsokktN*9}3#32((f31M=>HH&_6+|#AMCk6)$)I=Z`Uff{vO=BO8rm&uoTfx``&*8$oiDM'

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
