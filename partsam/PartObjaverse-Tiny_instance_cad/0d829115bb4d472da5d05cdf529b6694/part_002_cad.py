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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/0d829115bb4d472da5d05cdf529b6694/part_002.stl', 'relative_path': '0d829115bb4d472da5d05cdf529b6694/part_002.stl', 'source_sha256': '621b65f05cca371c9333840439258eefd480711d81fb8251c597275eba46a4b1', 'input_faces': 538, 'input_vertices': 438, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.37300461530685425, -0.46368318796157837, -0.3802955746650696], [0.35691848397254944, 0.2868534326553345, 0.19017216563224792]]}
GEOMETRY_BASE85 = 'c$}r233w03|Hn7#s4LE@#<h+#j!<{&%(p*BOH`98p{Pws+@XTH!b*vvD0Re{72+0hXppcQA#p^g`zW@0=tZlSs`l64?(BQk%-H|){GZ=XpU?At<(<jwXJ==2XJ+?lSm;y5t4hwly3*xFuRZrsBT2HOoK#hs95rF$$e~fO&0@w+^^+<R-~LDS<KBH=3mf1kO_rty4U38$Iw7dN9Mm!TrJ!IrD0<w4i4!7YhK!pqEXww~M~;b&vi#T)k>jJRpBuJr^-{3hs!^~UC;ylK%2+8Fy>DIC?OY1OR@rKNbLNl3ma5lsIbUvmFj@ETwTs!wA(kpLNAl&XY)scZeCg|r>2`V3Kh*KRd$cfwIj*^;spFSSO|{i`Le2?ceUvwcbS3$SzFML?$wzB`<q~^b-}M98x`(eBpJa38QIFK6NxJUg8_xuj{FU1?h_4R4zn`?*KJ5tSKdQc+JuhRVa)~`JGjKjBPkmb69GA3F_wbcxHf|(&UF^Z-qf{(U&P()--%6A7Qty}N&-Y=sBf5t#kLh}ZEl-atH(i{jd-!VQg=s`*&bi1Px7vkV-NTpF3%P80x1RV~2XznM93F6xs6LtaM&pouTtDeFi1XEU=QZ8Kmv3FrNV{c}=gU9H-K%@}=4XfZl6EbXe}QZNGHu9tiM|%whMbpKf58PV&lca4ej)m5@gMe+`j&Te{9k7sV$Vx1-GKAe8G4fL;Tr`<lF08zUp>$ITCEj(bPwN`w{j23GycMPHXm(&jG=q@N|Uh$`Ma#aTs`I=aap>DubrBiMSkD!>^YL}mbFK?^Ez^X^Of$?*6SX=wlr=%spob&@ufXi$Z?eRj}EiG+djkpJgj^8w7gP&B3Hk;cF1ns!`Gq*>?Zx?1wYRB9lN?u_wc2}Yfd}eyYeZUr?#YO9_zd91K+6kj^oeCC;d)demaNs-Q(sK=I9<iEwBCBhWJWma6a44zJW65n;m{%qkH(;oQG@3-_8B}EbGf3UEiU5_(q!>JIL<~&Yxw^SB;#J&-(6lfv<hB>MVP{=8rkKtnapeLJk>UqEE}4Q>JkFXxsnH&^>%(`lAf;`yqvANS@`EkmrNaX~03&ck3C|pWJ^$pO!byzIuku-}l9xqpa^<FZi-<7LmLL4L`wN7iD}l=ga+DCF&l&vZ-w%(RKri*!+!J?G4s<^UQ2V#;@qp^6H`<T>WNh^=-O`uf7?ujr8mCi%xU-jQxS!|3%;DyG!o>#-yY|HcvG|&SQPIU)`&dr+fHr`LE_V^+YwfN{&-MIg9n_ai#E$<o+Z2w7k#1<0-Ztt#-{rtncREuFfId!>8qy2W5yaAL~-cUPpQ5w<lR&OK!13_wdcTtyhrqF1z+5*AJ&%JjVL&b%bxeJD01+_`O<+?%^xzs;7|ln{A%p%KshZ-2Vk%*)*Ko|D}n$PjKy=8I;TVZaahqk?|<{w7i!6*Ku;3<!i2y-}`4~vOYbo+%Y3l_wZ?X->Hb>Tt8nDah&zt{!IPiW&xYOT01e1_1%85Zx!ipqEE}q^0fjse>G(G0oHfhbBuaG_wZ?XY3$GW#4nvw#P$>I$4i{Ao{*O59==hv_%fnuJm>r5ubp|I;2X#8ka?i7Zbm+r|E{u!S>J8{0)O&+6n$D=k$*eJ)~~GCOz!`pFLl^L?*GQVi^tgZr~Q`t?tKHkl+%){ht4NO-~4B>GoP&e%~7sjp}$ez9e3!TqEE}qJv$v`>(@>uJI`^!H`Z-(=4;F3Jgz<IeF?tXp7cH@_-^@=Rh@c1xpbZFSJZcpi+&~gZa=)Qk$JjNFX}AYucXNNoUd(rd6DkrpKrK`)VH-O=S$(`$h=GRed{Wad6#<hTrO8n#Ab5;5q+iJ26F%LH93^ap09hqh41!fdcPHXTHZ`;!__aRy}wKM@Qr?Rcai#j!u7}XqR(II)9XTgC3>vE)sKEC`m`U)1KJzxdC})7_1*D;=db9~@>1F(GXB&HH$EfhgZm!!-F$GL6n$D=u3zpj*FWjJ3%=VA;VUa@9%A#S^C;@O;|{)2rYMKYlRkgpKkh$x{t7-VZ?^02)YG%|r)<AfR&{lJte4fCp3ZzBrz2Nhx&5yMFW;QfBY|Ackh;W|Zg(Ts+3eDc)Z;5C%4W+;U23iL@_mctl|*06BEGL@DRN&_ZeAwqTjSe6uDtnhqUPnRNt4OC(imOFsi$5Vc|L3L&N^Jp7;unnPdcBZzB|4!{}g?<d`!!OT>j-Vo$)C6X8Jxd9?cs8#8;AEB=b`>Xs)xqJsx*}8>e(V0^c2v@a3|_4{+D9K@NE?h`w_25P2@B(|&NS>x|=MonaO_>t1tpau(YTbp1ko_x^+Rj_AAVqc4|bao2ZI9GT~czSeRUndfLP&mulur<lW>^{OxJ-af9~DoE*GzHwV3`#kF0%uMb&VqHmn_j<vXx0TK0@_D-q`C0VU7G<4r{nc@@jxp99b&i|Ub(Zeoo0Y4~BJI>SjrdaHF>ZXBRr_$hZ|lLux`(fI%3VzUZhmpDetC6uXa7&|l`m_oBKhw5E1ey`%3n8~eYZMarL*JF_dzc2(|tVn+MwigZrlZpa{TDl>1>{A<)95-zA?D*2BHgt)7f!H$FDNLFP*!N!|(3%^40eDoc)i<OVYUOh<y)v{=zhN9LY(}{+F?KUK-bK*cTOjx-Y8s(f6|BLQ|amCSR4vz3h3(O}|L-@{My}l5s7`>K<;~tzGK$Z^4&imXZ6gdNezg%}46lVY}|(8&%toeJrVK!Y;NQ+<mS0uI}XW%)Lo|7JYN!m7V18vJUUy^4U|8+%H7moL$P9KNoAeo$Kc<50Lys-*@?7Dk*P#mBO{pi6KsV3BI;YA^Ujp(bN?7xKdyXa(@(k^Fa$|f1pBA3fm5J-%{?Gy_xu({m+qnq~c^AE;p*Oi5(Zd*V|noKPNs)X8XT!D}eY?UQRN1UT-9%dHHhSJZF9V;d>gJr%!7@o;RW|#|CDz<$c9!kUZ&g%4`$7for!~t;l!~ed(uG&i?%5O6$3H!2YnY-dxSruhbnv&fl2dWi{76`*&<5KbQ1h#hq`nQW;*pR;4)Ew^5?&t>ngU+-Y*YqOXP(k@NKxU0TZJb9WB8esc5rOSpVOwv+y3{(N*Xd%o(a@C+~Cx8V(vkNJM^BDNjqzP;S+wFEBD*be0RCHiXjj?VM$-*P;c=eA2*$a%#D%;MT%Z9#^Yuf`mA+NVdEN$h#ap_yb{Nwde@@67hYyna_$-@Ol`e^TF_SL6MKTMy0u=36<shi~RZ<gn%4c6*qSp?mmJVP*zfp0<NFrPo%j{-S}zch}M3_a=sToUiYVPULwgwwvg??H1EAKE$K_<)$HIUirjz6nuIem0voMb(Pp3q@O<_&sDKsi9YRDT2kvJ?0M1t={tL7DVHbuvofN_N-j@2E(D*B3-xfdRct%ZaVPq8+{wWK>)G?7<K28Qa08pad*2Xzdf!m)OxM_a=>1Cc>HSKpm7C1viTk1G)BB-s)TR_JPu!m+IU|LwpWf$1pWf$<klQKTdEq%C`t&*CTNt{Py)JJ59Mpb0n<ssKi9UUP8G|!+u-DzZS!@!?uS(tyu6^*_6n*;KG|u1H$>vF)%c4)8%SK-OF1Fq1^Ih$>Kb6hXohJysJ5Sg+gUqjef9<+Kt}C5~z<*+XBKUNEBKH}xm&+gXAJKQ`KPTp=as2`FF43p+E_2h;H1>Syyv|(xPa2y)ogY$PoHvR-oj1x`Tc&g49rIPur}I@Ut7Hb3Kjzz_Pv_g_o8cL3J??y7@acSBjnCkGw|@o}aP`ymh3M1uh4fA7O!j=~`bG5J^-F%b;|uE}>OZkQy8pvIu0Lb_CHi#zr8QWZ#f@vM`$V6v`;=>17Ml-USBgGeS5jYGZz?a9Jiz6H^{?pD^{@2%EXNnt*VGr+*Gg*hgKR&f>w4;o>wVFu>wW3hh=W}FW8Z-K;(mhkY{P8!xO9Jm`r^Ka=)3zKrA~7`-ER?ny5A!I-9CqFH|+C>KHcXrhrh-7Zh!7sn8Thg-FKqCxF4k*seOpOF7EqB_~Jg89PaO|@5OyK_~JgBdjH{JE+4wTH?^I?9@pIugfH$Bnk5_Mvd5+Smed#bGu2QhUvb}+`r`hoa{YWRn<w4ZHNUHp$JXQSSEtv>WAkzMy#?Rh_l7U-hpU~DFUq_7_JU9M?Ulky&U*vl{Q~vH_X|eO^n5N)`o2T(>H7}NceQ}?alT4}TLtWK>H8zmr|*xbFTPjOzVAogQ;F}hs4u?H(yl)`&b0&WKg)NWV2|s*j}v^_Zf4zeC)wk=?-SvR?-}L5PN%r~(NByL^9s58=|1p^4TWs|ZhsJbw?Dua-}Cyy1{HDbgZ@u_@%^=Sr^gxcv+(|%`r`X{b@J&mTszSB{;{jhvh}$40r=wg2EK^%&VIM>odfm7?;OnZ$WOUE>3*i*yZfK;#qT<dsaHQ`kL&K!!WX|Mk#y-CcU*k0LVfXj6>~!RIktZHyBhdUd_VKb;PY&G`uz{}#qWQ7{udoz{ElePf(xuqzk@QD<rDvj@2N`9y-1ELd_PA0C%zM#;eUyg7rtkcqIz6n>!IJpX~t!)JoyeVjQg5%RK*7m_CF^{c9fQ?O3{(br<}HF|D)>tDd))6|F2Iu+x+jJa-Ohq$g|>0gw3Br4}(7k-+=B1-vD2O?gL)~UxB8BuYfN@_keA^3byqj_%iqpXjMOlZLI>HZRtWQ=2-CobSZQpcqw?56(3rE6KlmhE9`xP*R6QdiV@Ig=<DEU@H<vSLVH7B2lobdf_4UX0yl%c0B!~jggy@r1lNSt0@nolBW$i{MKx$0Xf1FZa6{<x;D+GV&=<h1!9HkbaA&lI4`FjZroH+hY>u&Fi4~Krm=BEs&j-(ejsVXAtI%k$3Z4#q2Rt1-mAM{M5jIbO4h2sEPlFBzPXo`eVm5RnbU1h<I09jFU+7S9UvL;S5^QU4a2PlQ+6f#2ZVqh*ZVnED27-gYwV^e^wZWC3{@_aBrx7-nfK~*T0GE;;_oq?_o6A~J85#hs1`Yt%ht>ht2M0qNf`h?rp{>Df!LLAlU|aivUjYw-#(-^|3?2j?g0OiebP3qj)!><6`#$g?G#R=YoD4pQuz44B33wMc1v(#`0#1U?0VjdiLRIiu@Ji@(@JjG<=v44>@G|HW@G|gH=rr(B@W;>@;E%y8q{ri71;XZ4(7E7M;C0Xi;B{cliY?HOpbNksfoCCXeh)eq{2q85bT-)5k>GLQ!O#fsU~nkH=2xM8!LNc}hK7M{4FSIlZUb!&ZUb%v4FWd;%h1|j8T>4?68KqgIq1{ia^T_!n~On9fQx}8XesIOKb!raWx;;nr=-W@`6-0WrLCw6tq!dWt`4pX4FJ~#H-^>+HwL$a27_CIJ3!llJAivaUjf@X2yE*Ra8K|XRt$iSh7JMSIumT`Jg}{?;L+d#h;FE(C$s~!8<S@@oX5Yc27TL#o>q*qBFc(cR&29klNGzH2)D|;ZN(@nCO{JqiB@d1VmtIG!sY|eMDPLdPAfJ;7ef=li@|Zw1aJb58wY(G90#6c#aQS-=-c3d;2zL$a1U^MXjgE1a0`UZFWGGc?FH=$?gj1-4F`uK*Zxe~^+(t|%!={Qc<2OhJa{2A0i1v~UC6ZiLWIrht=J0Hq1(YaxDa|2yxF?ONmgutt^scVuY|4uuLOUDuz3M=8F&GBKJ-Jdt#iTi!74Nktb(T?Y@Ps}3Z4KS0i6gQ0UlySf9O!?MDS4XWQ5Jrp;N)r!ST>Ia2#@tN7$SI{Scf0UW~B$W9TyQ$KXWh3h)ZFbt1y%b<ia6I`Bq>&0C<G!CSyPtXOM>W<`n>+o8Ly$gpCc6=~2+a2j|oG#$JboC@6oP6h9T?gsD1v35c=@J{enE0Uq>p&EEScr|n_*p5Y3EVp6_bRKjOcpmtDD_*psy%l|+eZh6CsBcA0Xf3d<)xkBv0SKEbLo0%xw<6Gr8qhl6I{5n<&;W1%{?6uN(5I~UQ*!hl$qAdE#_wu?p9Ysk*jxcx8C(He23irUSkcRhu2$T#>OW&ez7?CS*kMIBG#{LgGT8{5Pg(Ib^gHMo@V~8iV8vbNci`_(<}UOW_%8T9^c(Pf@GsCG!M}hXL4N~30^1V<TmJ^zVRH#+DL;qpu(>SMA6yn(3HmI!68Jf2UGQ_@+R%pJ+TaGz7r+g`jiIf<jloT!9l=e(EudY&Ex>J|y})h3?X2hwjezz7M}S8{74S&#H0UJoH1PWfn`c<@9&{LV5_lMR08{}h$aMg;BX|I~2edV~2RH=!0yqTR650^l65Iq@7u*C~5Be;)9{3rkKlmANIcO<xIj|qp?oWRB+2-HT?|uXS4*nkcBlvr;3H=6af=@$lfp1|Po<`VgKzD!*@HT|a8=#xO8^DXKC~rjtD@r14E(3iATn1bP`W(0lxCXQyxCXcZv<bKYxGA(1xGDHWgv}kH?Z6$u-JxB;w!Q}L4(<be3)}~+AZ#83jRKDWPlUb;w)K7RMDPdDMc@y>YoMFJYrwmq*<f2wfp>$COONlT$Dv<<kAsguKLZ~DAA(*29|C7VFMzYanb1$cncy_&IdB>{6?zt&3f>Dn58eyTfL;V=fIop=2Y&+2f!+q^fODZ=fpftH&~L#7;FHiFz$d{)(4W9X;G58&!N;I?pg)6c{S$l#d=L5$_#XIIXmLM>e+B;qEd#d0=92I#f=hzSL#u<!gR4PnfvbUKXnn8@4uUoU2Z5VGgTc+ft)R`pt-u|iZNMGCU7#<4yMRNXoxq{seo!B{ANVb3H}G5FLC{yggTRr{*T9kBXz1(UXz*xgICwO8Ec8wASnxP#AMiNvyU@PicfsSKZ-B>xW1wN+81NWqZ}1rKaOkVx;ox_m-NEmG2SZ;54+al}b_UxT0UijBg^mQrf@j*fh58k%`qcmRzwmhc&t98J-2c!+{7e3I5&M@#R$cDPqp;8t_VY(7X8mX1baU-HyYwHZ$C|t'

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
