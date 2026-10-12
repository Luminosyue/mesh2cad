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

PART_NAME = 'part_004'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/4ca574ac76344394b73acde0ef7b9bf4/part_004.stl', 'relative_path': '4ca574ac76344394b73acde0ef7b9bf4/part_004.stl', 'source_sha256': 'c10d7aa23dfcdbc0f0b2eda35ee61540c8a4b34a160d5c16cefc75ae456d3ee8', 'input_faces': 537, 'input_vertices': 280, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.1237238347530365, 0.0798025131225586, 0.256838321685791], [-0.10200387984514236, 0.11255034804344177, 0.3566492795944214]]}
GEOMETRY_BASE85 = 'c$}r133N@@zsFA!A(N?MNK98XBtmFVW96u^2vG@w5F#n1l19)NZ&C9sW+lcNqNYeB5e|x~=_a``RMl0b=2lHL_Bs3e-RU`R{oh(|y_c@LzMtQBZTsx+K6~$TZn7HI*`=7bf}a}7jC0c;Yrcx2f4mfLWpr#}($JXLkwGI8lAV+?!q<PKF76r;8W!oKj8?|g9vnL|Cb4#NOYN3%O>5V+)Q*c!OiCO$VnBT2;8@*nKXCZS*th=3Ap;X)-`4)YO&ip;Gz_R~nPB-p{&>6{f;B4b(4n`g&N{X~L?6@ETXtQoy{y7lx{S!uYqi@c;j3xmg`c{1fbgyD-zyY;_i(hg)EE6&E4m8bvN=rnnwM9$UTa6(gztFK1=rni1pUAJiSVPJw?;pe{>~KR*|$kt*V5S^e(+w=zt+E*XrKCVRrH@QI@{=5*Z2tE(O?U5Rhex!`qnI8(Ox|`8RKmC>Y(W7b}5W!evI(72akoX?j9q?W9^-Ye%d?~zIEqt_*us>Klg8=y?;LXw+$2hC?DN~?{*jS_H4i1=xe_57{6}@+K1TC{!}pL^RvF9y|(zY@Ex6EL_f-~g_ws083&E?p#JlRXdiuJ5Bx@TazsDQ>oCvFccTB$l9=c2E$k+L?0$@=%U#Up+*IK!pZ$WoQ!Bv#bv67B*D}O)Ps~F<O;%ujB6f*!Y7dX#zB?8Q-;#R{*Dd9b`Mf$!_^EB1VE$dd!hANGg7FkOkZW2E+?U`l(f^p%SPzdsH2Lb37oxp2{N3{=KV_tt2j$5{%)`$K=x51pF@9x@BChNBDHikQ{uKAC>r>p9pk8R-Zye^K_`?Fx{z5nOe{GoP#~RQ>^pje*3+89)3XHQ`T%pmoHc@e3&O~4x2DZli{iGTC|L|A4(U<#F_FvS#abwYs_I}^<M&H^oOZaMjS<HjInQ5F#;88JtwIB%nyweo(W(^eWQ}b$?$I~iPw2!W3!F{}OAGy@Um><9L=s%+v){ht0Ien$=a?F3>9IT(SCE-u<664Vv<**)VdSLvQ8ev^Mn_OV>7Y#w)QYm7b(O(wFbvHjl|0_FV9?m$!uN{YZTVDhBW%SEj(a*6&F-~R1Akp4xc?`d^GxDBF7S~mNyq9ZSpK?8G)ou%4y}cgyeeGtu(J$)X|2nSw!!_Y+1#ZaoKo$L45`PkY^z&P|Uwe*WzZ^f0_RCX{>%tk_m&ygWZqlKBqWzJ4(T|pJ4%hwj62>#Rxye_LzBKJ$=_@XQ2SnXuI_BZnDd9W5D35tdxQBU&{~rG6_1KTGtFW$)YUuyj7dV%A-a0DfqW`gXG0xJj^Tqf-&w~GaJoZ=2lR}eU=L+U+r#IHs;ce)D*#YEA{yX33J5GOyak>TLd30#4@GXa@;<{(&7Z`o@yC9KQ9s3XZ_g;<mV+uukrEg}w(Rb|agZa6080%{2a`baC0PD8rr*@-nEq4Lu+r)I754kDmf5KVpuU-XMx1Y{M|BE-HpOxw2x@y^JxbHo4u->)>i1td{WUP}>KZ<c`ISKhjU%R*j^AOXg(A0iTORTG>9kK69k3;)D31XaT_&vMHZ>iwEMD)WsJa`Q5OHOahk8dZO16d={e$gtd=e&3^9><{JXkY!PXm71j$K<PCsp7iYlQHPWD;Dj&KF2&)Y$5Wh8Bu88G6m;Va6rD%w{FkGdK-HZ=Zt3`)4tFqT+b8NPyfU;9xc?*ZuGTzH!*KRr{THa-VO7X(FE;dixn9CqUXY%Xsn059Zc7?{<1pH=qn2sWEjUIeYvl-*ORc{OSDBleBaQPHN&~LyCwQLnS=FQrx$V+Z)WOWURU~R{cmtSpRHpz`8=QH`<}AveT=8SAM##4kZ<(mb+u7t^NhY~Pr|&_Er#=?SdeKvYDmvKqpuA~#lA}&gZ1xH6Z3px7jg~z-e&aWIi{W3X*c>x?>;!kcn%b`U(pczh3`?8-qms48*?&@<9DQ0Mn7=@n1}3TILDkSp}qHLtn>J5I6r%OW1sG>fO+UXN?g~vy$pQ$p4rZ)(CAxMwZi)3d#v=W8?NCzzq}vkl~NMpX*Ln#3^*X>L5Xlj`=wR!UQ}??ZuHgfKgIa_RKoh%>WcCI(*g7I^*-#oH%@4u+y(1l_hXSOwa1$SqW`|7G5=TUiuRV*PvQI6upj-?asGV!hw!z~WUT)=w{YKI-W9&O%M<<dxRGb{t%s7aFKlaUruM@la2}?e!*eI>mhdfaT4Me4e3QQB<AU|Z_o5=7=an|=Bh2Tf-wv4eZ}zGJqpz$9$N0~`!gFfFCDZto^fhAq(V_Vm&*c!DKh5UbjDB>ZDELzn>_%VR(irn!A~4_Rr`9@w_o7ps3XQ(jtG1YDW!@u<fBjk0cr@?cc_u%>1NZTEHlE8}P9WFS!@^gClJFjqdKA8^8}7>o-Z&qg9Kv<8LXmgSWSh}fUcaAdypKgbzkgXbp1|{N?SA+>74%at-)8dVJjW#z8huSk$9g^yVDja8Zar94tOv)Vbn`qk2*<kZxZ5;NdB4=v>xJ*Im%~1~`i0HtYu$q~P4h`#9a4b211Dm?w_Anw(<__KXX#t_#bRFs*2nwU%4P63*Fpb0XDn?OVEu$&Oc&!!$+Q`LZTlVg2RsW*KA+3hS>IxPE}sLx)(gz@{CYSC+I$UvV|9!_B*$j-)mnXVF1>1HZog$6=Knsv4;K0So^Jgz5_y+>g>~EiFPvk?!|_~hJr?V~<aUg+QV8x#NId3$i(TZhb~u`E^tGfwtlQNKuwPmYM*Gk-(O&giWi$HnJzxDZ6Z>LuH2mDv*e~hBaBeJ&z<NlZi+Ol~_e}L>clfW4VV-X#oBY%x{cwKr`-r7QSBxiNEB4E=TLng6et*|KE;O}QbNsNc_s_w4_^mziuDXKfV9Z>b$>%wyR4<NsXx0Y)$ItK_ulO0xx9csCchf=4=Zppzf77P$`8`yvoQ-p4b^!W$k&X7{ZsnQ$_TOPX_dhH&`q3j!V?Jwd#rurI54p0laDVMR@%?3HHC&g!_mI!Q=wEzI*VSgG<{AB>@7Ep)Hlwc`?v8m|a_qd(k3O>%zWkomup-)*8;1K*Ykh&ySIgGJx{dS1dYDlT*Nx4^_?Mo<IT`F_8mC&=2hXW#Zs<QU7P<BWAy)$@^wTX9xjZXiUw{2N$LOoYuG)-#(fjIi{C*=f=&A4>I|gPN?~8Wvf$&o|-ot$vRu|*1cNhM^7I<#%j>PycTo=B@r9b)^=wmnfvVS@M(oc<=20wI`sh^_vhsZWKZv!2|*Pg6E-mlKujDGa_yZGMs+Y79p!i(lycOr4F+RvEAsdg@h=Scn$_))$%&s&x)F#6W_J7B-~-oU;ap99~i2l`)f#Afu1`mg^nzGvAo(LSxFSkKl+L$DwH(uJ@5`8m#kH+#^}xiqx@yA0;1(oY2@-?9qxQ)2?|%X?el&#Z;}mDULFMQ7JxKKm5od(;W6pVLd>Z&fk=FjtIo)O^e{e-B^{OU3t#>N9Y^dOyefFPeb;o-`Hn-?b9@X}%KY{K#aCN4_V&x2(YE%l8fCb_U*WPmDr)`J9@j;e4)=i1~E>3+uUIBa`n~5QX>E0r8m6_!#ta=4aFT)O`A(ea{CN|G~R?M&J6pGM?8whpi)eV;(x*!+yCo9=R%YN8UR-;J5FAc^e*T>R;)!0q0DG_89*LZ{&&!#(VFfR_LG4S#4XtJfp9EG#AhJSKBZ@-Yu|B<o6w}PwiksQ$N-|H*NpXzg98N=ogKr;114>Tz|CZ_Yvh=FXSrgXIh6vxpJx^FQ2DM<YlbeGQPOK$2Q@8;D;aZeJ!?vc|9|)7UPLr*GFTWlsKMm^yTk?i_W(}3VfesxW7Xt<r{tNsVmmu@N;;-+V?P9jA#88j8oHaA3YujU;e(aXgv?OBYf@1e2m}y1N2|wqVOHF2ICy4))@D(uiez%nsQ%^Gj*3O+qnL%{=4xWyYm>vQ*jR3SKpLp@~=i`nEG+fG_}{3L}C7W?G?U!&zJo;lr;FmXJGuND`B1^wwQb^{)Wxuvme>Nb=$^l<2u)}QZWATZ!m8&BQuQa%JOE3*$=vc^ZAoSn1`W>IDe*GLO;)wkZWpF^ndpx-b1>?p`V!cXn*G*{54&KFMl7aPS}C<cE1Yd|4Rqv^Z7zsNSNubU!7)GTb<^kDEh};@mAsn8vgX9oBEH`|NN(~p^g4mfBI_Nu*v`TPhVx66s5x3PerQt+fR9FIdXZj3-y%(b|GI?py$a~$-Af<$-Br)s8h+ht}*Z&)@#V$Q?tn5lmDdtPS#b=BiYRfwf=EqJ~w8QS>ItMT}zS6k@ZZvK4U)p^Ng8vJwrZE-bh_e-bkKGO(0Jt&!LVZ&mm_~w~({Qzf*rE|4!C3>FUgU`p231oS98#Ez4}WmL!)V>zQ=@oB8z5-^`@zY4REJa%u{BIXQtkoSZ-&M@=G+BX6N@Aa5c6Oua<@nXG5hRbf8;qcESsY%*(UX4BP^?8%IhA2Z)$=8^m(>(k^E>Oyh~c{ue`@^Eqzbp$zyyn(uwyn%d)dXapItY^~o4O#!_T$WnekkyNsbaf|tlJ!iw{>6NMF^}Y<tbZggq|PSKW**5gtUo1>pbjCAAg`r<L;i-jBp0y0NPa_oNq$4t^Xckk$m+ptx|Sfjll4rxK43om^MILjJxD%Eo=u%Xo=uLS_9w@XhfoKThmgOaE+sEz9?9oe7m#04pOasb^?bT|Fl%w<@*umiE<x5a>3Wy>?lO<$1FR2{r%<irDdhgtNOFJjU}`_|VDeJxJn~ZVIqE6$Ir4MrBl2^yo=ex_hK$9SO;;zfD_PH^>rLj<KR204*L3m$vXwf9Y$ZohKOskw`%!z7`;q5Sr;+E8Pf?GMPmv!{{~$ji>-lsoX2|*vGwJ%8tbblJldjjvH_7SL@5tXVkK|#jhcS=j&a68#kK{1cy~)$46Uo!aN2s~vT;`H|hxH$1J)f@sDF0@C!A!b7B|l{z$v?6FiFqV%V!erZBoAagka;AxW!;$^M(scjBTu9zk|&aLse8$LnM?9-tbb!h$uE?Dvp!@dUGJ0cGmqpv)_Ke$c{S_R%p<uM>t4(wxjE~$<POwU<W|fhIgWK4^GM#odI$4JzQXznvq^qv$a;&JbiF~o!90>rus*>&l4r7>$vl!jX5EY2occbwIk^?}1M&yVBe@UjIPwl^Dmj&TB->eEAwQ(vB0HGp7Wp#k%giG=gLMY;NFL34H1kOQkoAYmBe@RiI?N-vF6+9?Be^T<uFNBO5$i?FBl#rjlguR9!8)IL9OSdCFOxH<-;%#&9?1h(4`3e24Oll|9?2Hg7Uq%sF6(!hM{;Y{t(iyiB-WFdM{+jnY-W<2&-yU)<dbt)=P-}txvb|hkK|C+q0A$>ChMBaBe^{5^2{UIm$fhRNN&WsHF*+sD0wLJNZ!hND>F$x%z7vD942pOy_tC=f5Cb#Ih5Lz+?07FS7Ke0T%PJh_F^8%Wm%VH9?7*?*Jd8cJz4i;9?6SYZzUh5?j$c`o}J|Btfw=N<OtRg%p<uL>srhsxg_h7%p<ut>*CBK*`2jJ^GL4Dx-#=fZo|3_^GHr+oy<&<ml-mSXC_@gCr>9wP(#QO<XY5<<XYsCR2Onda&f9cE>3o*I+5MUm8qr4mC0?WLF6{%WNH*SnY@fT-jH<`GwJ#z`EzmzwIex%T#;IpT#@WTEkSl6D^zFY-ydgY(zTdU^fgX!X=*ugX>t&?899g?Mg5E%MIKL`MPA7~v&b`8&tM+OJy>@nSEas3evf%1d$RUq9?7n(U71I+8*4Y_kz9p!73PuLo^^ZXkvxI*XXIJbmE`Trvy!}m^$O;Z9L+kKc_i0kU5|Mrzr)&->`L_@doYjWQmjick7PgARmknB;pA}UkvyOE1oBGicJe;v*-qZZdK>dd9?3eIT#wp>+=O`~`>=k8>_II<F2g*My;+wc`%&wY{m9|eSaK}$NM6T!9WzPZ$ND()>?3Eg&SW0RlUa`>H=(v8HzE5_Ymj}&WvCU%6_`hIb=KbG`qUQW`s7&ZSn^ork-VGrI`Tg1aYM!n%%tlN<R6$v@+#Jo$?d4!$?eEBsDb1f<O<Yk<O<~K)Bth-^GNQ*x&?VGbpd$+^GH6#dN=tv^@1Vmugs)tA-RxwB&V@nMea@=MD9)wq&6l8lB-eu$^OhExgqNSawlqEawqZv>U#15@*%2?e29F3`l})9J!aDN8u=RYNZ!vnjXa1tiadzinEDa9G1;FQO!g-?q^jhG<i6B+a$oX#>K^iXvW@x+*+%}Ade4yc2{Y+>n|zJDpL&eEpFE2CHTi4ik=%{-N915?OL8z-rFJ2!<ap{=<aqKPszwg$?Bwk2@<07=PXGQ`^#{A@e|q}w|I+*?BICb&^R};|KNy8|b`|eR&Ts$IUovm#Z@9{T0V%DzQv'

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
