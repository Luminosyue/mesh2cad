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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f121301624174b179ca4d50158797b03/part_006.stl', 'relative_path': 'f121301624174b179ca4d50158797b03/part_006.stl', 'source_sha256': '24517f5a1a3feb0bf3f9429638f666178101c8f03c788a6830baf1983a4e6313', 'input_faces': 556, 'input_vertices': 329, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.0805903971195221, -0.2119203507900238, -0.28906795382499695], [0.060453638434410095, 0.07673311233520508, 0.1825210154056549]]}
GEOMETRY_BASE85 = 'c$}r133yFcyT^BknIOavB*&BpF~yV^w<)M8MHNL45;SIsdD=zILyE-kDThSNM9fodMFl~m)KJ4gl~VImmFhj~{r}UP)7$$z_qo^itndFj|8M2pYrX4TYwxqq^M$p|?p{>Gzp~oWr5<VBd^JtA{8~|Mbi~N$FZxA9RU0~doSRlieDyC=7kBuieOPxlZL~JQKRhC;-$?)Z7XOC*gZ%?7{{4rIj2_u%=;y;mhDRtrw9nwE2!|gvu+Q)a$LC75f<gi<wE_YylPv$oe|a54Fcz)Zb;O~TaYs^=TBoevdBn-LeZS$PeEutbw^FUq3i$ttJEc^wH+P5poo|%*X7{cV$2RVEva@fLY%g)FGf$x3sX?Mvzfuy%mhdu3;{Vbgeu3qPZ|vLZ?A!AV5#PN1+4d&te~%8w_`_2XXLi;2BTl|v<qUlN=mv=s6^uB!ZeqUgKWtNREN*q-?<^qwEfurxRK88KU_3s5%J@z9$UUM9${_v)AB^X9cYF>hhWuR4aa!WU6q7vI?s_18(KX_mwcc+N9g$yrt=7%c7*EM~7ypmz;@g{*-019EQ>V-L^|SHGYMf@Nr?PI=9%C@Cjmvi{-xzKe-yZ&0#%T{;Cwa3EJ1xG(dD%MtzDwpicf0tOzH^YbiR~m0)=u%Li<rC;-?Vha`eypY^GO`NZ~*3+@gH2b{4w+|G7IZFce(gxJsavOAa1X$W67oB+b-0W>l!T@%ew39m%yJCj(W(sdc(i@TBmx*TjFF~cSvK5C-%@D6<<pnD89aUEb?O}$-3*`^}~E~|0=%yUJ>bU7HfieWh;+7TRKagwWIZL-GS4-m;Udo?3XwReu!VVzWC<qpnVeOdTI3c4Zyz8&q@7ggS^pyQU}!A^*z`pUPUk-&&H^e`=3jm?ML!qUI}*bway*3i+0F^eAc#{k$DyOig)(43?K0=>48!|)<}26DZ_d`)Lh1y>09To7hk(JLh8Y6cSEjk_OFh5PT7Zj_x2Lje`(1R;-8H@Ap5A@N%6HuH;>D8I?t8-m~W0?9tnR+ehi<ySeG{&(VzR&GO4fBn|bIP_-3l~*YCZNIL4K!*iTXKu)e2*<#VQQU5EH)ggefeSChoI#BRs>dXAJj)K`y&&-`cB&)+`xwZ6MD>ac1w{1)xumtP@uXdE1Yc?}6WCgW=3aY**p<-y|X5qV`iwiXen^QjS-*KA+uZ;sE9yqST$5#P^G;#)^GLVi|#g!wM&i+!|qHtM!uJ^0PLNd9e42OpIDc$CF@MHQ6(Mszit56=rCKRNfyx>#%Ol6BYmWytw$i}ptRoLf+z&)<n}S>71yGGqBJXW!UbQ~GOPOqMu$f!DYXOskCZs#`nEGxU-8dctY(4SOA_Tg$}<@N4Hq-SXV~+kc-Mb^FABql<rM8P1K>A*jzjY2w>EeJS}gj{b)Hrys)j`<ImK+UCbe-P)EXiLd>kA^+KYB>#GPBIZ@>wXBzR(v<Vlb|D7Wo%I%V)lirI+7sOO^p$(DUKbjnZg)*VoNkq|-;-jo9`tQPD#`dQMR5PqE{qr7JbxeS6?stV)0hy2@%QPC^YG#%sY4^r2+VhK49@c*LGjMM7P=7Uc5E`v$%<XEE(daA{7Z|X4#&5`IF}^IbuC_NrLJrhbj+(+G3<*|*`yBbv4QBn`6}`sQxJ7hp)#(U_5%AW5cfGf*&o;4Ge+vuTzOdP)2dg*_>FYLPqAbE56d9_ngKZ9W|?w-)W(&<|K5Hr>gSeEyo=BKsclz|jn2NkVHoB$s)f|Qz1#=MtM$Z0jDJooJkRWSk9;T1#(Md;#`)Xi9sIL<Wxtr7eNg9T--vI^_bJYSW1$$wn5W`fT3^R{_4nH5>|3AjM4fbMjr(to$B5IW2*#gSN#>R5n}s})hn-h(&NRM@@n}EF`0dsDq5f0txUaI_jKXzfoHqBPIOjM{qr&54XW#m`0`~RbN86lzt<)OX7nV-V4ojVPUx|4o2H?DndN2DzyT4p~dr&s%ul;;l&Sz`(Sj2ghihQQdm+M-5$78+^kK)`oF<Ij1TgPBtH(uhLT=*1mqCUYmM}^}4JLrbYSFhg&`I%Z1`}Aoqsb^d1au{dV2e_}Tm@2+~z6at@8trmU>YMT)Kl5gw9&&D!I=3AELCz;@u4^vmq_NHr->7*U_pjRJWSrWp?l{k`jfdag5BWDcif`|{7Uxo}r*baoMZMtvQP$=Bv3|5u>cze+%;kQnzls&#_|5AC;^BU({qRuE1KXd|C64uAA&GCZri*Wu=;CsJu`l{<i{$IsfCW-F!^6*^ZdSn$efYKf{p{yw<#Vtve0%R%(tq<|>2J=oZWjNKz{N7YnG2-9eQMGs@nd49N}TnP$0cutmcdU5`%327;np$9bDIV5f4@FW;$-^?<Jq+e`?%eTMH1(2xWqTomc!5H`yYwpQ|5$>tLY5*d-|-DIP+p~-A4oA+s92oef%W8S*{lRl*=<D&efqZ9(`0Qz8~aIknx)#NirT|b0qu)A?qbh&Xc%q=}+M|N)_LTt}nhlxD$LcWx2#nT_C>Jr7Zjdg};&O-t@sZZ|8>Jt$U30^ZF9=Jvw{6_+tYkZ}wpw&Y>PZg0F3uAby!#h##rLFBCUNt{Zku;+RFs!!Q0#qFncJ$oDe-!#UuW{zmek6>cGUFg@QU;=0}&<n#QKGEOZbMtq}gh}`G2%10!Q{^LaSFKvi#?_E=TZAvZp9ygas-j?h~exAHsCw|{ovR+!TSGexk*5VsOa87AgYMhkurj|zk4M7u}*YR&ZB|)xh8T&2r(8C>me4xzN+#N3Cv1h-ZAb#Mk>CWqJZaoG6*PJq6>xq?^uXj%P`%D?Xb@6<}uX73apX59%o!8NRb1(d7`ef(&*TNFu&$EB&T>rKrmEm7my+ZowEz^!T`$g}sl743c#n)<7#C<+!x8z5^+EenQRe!e@d2Sge{o4mge@oj}@N<|pnP;B6=jHDQJQd$qung-pdJ*RJ`bYGySyb|7><Y#@7D|L49k<@O9*n>>@H3{%Ibc41f%uvJx5Jk^?^9drmGHaoz<6?Wk^Z)C=EEPpbA|K%)hf4vf4!H)*B<th{+7@d@UJYB{1`EJWnbuhion14CRXBfdn~?fk_Y@kjgjZ5L)h23My?TmaNk7deXaNG2jBZO^3Wgz`+Zx6P5$oP2ABFYwx)@%b+NkCp=E0I)zW|6*<_df66h(uHn*tDele$Rn67*~pO>t2+sN~YzAsdK>x(ozN402i#Mw71=Er^Ed~Va(*A}&w`<K4d)5W*kdyD(R-jObGjE$>spZYKc&qW))mUCarzf$fCmP4Mnk9J9gpEO#|D<iTgp3`EyXN#YFa*52-+=Bl17sBtmU*ecOd&zypIA21}DebpCvcK%{JJ7%7Zun_WB#wEfq1<nbs*UH0Z+Ro<zrBB1JZF5h6Mk--Guoz5+@DOhdGa|uSk7BLp&!OMq#^um*uVPD@wm^u=p)zDeDcY>^uvwud|-@%|7`DkneVJ65=W13Cv~PJ7L@w5*7^zKnKcQ1S2vvJ%?}{{q8qY5wa5e5r-ScfzN0;sieDl_?st0h1{uG8ej5A-pUQa6YY`Yv+<f?f1td@Au{(IqY&911fAy{GJ4=zC=pV5f{`Ew;uK9~8@y$1Rmt(!oVI33m;JLqjCHP&INM7}T;`shMYc%{h*H$=R*C;jze)wilGyNUroBbH}ThDA?IoE@BCKY~-Gq}$#7%tC4X50)}S1sn5<kMcF9KKgPj>mfcb6@P*ivI2mW&GxY61eW6-MFt*>LqojpXiBswLJxY!vJ~SFs9<YqWK};Dy&Oitjq6fk+)9*;M=tR;t#0j>RWFN6}4B{;o{qIUKwZGpw4$Ct`<L|qO6<Qbv))fF$w-E4Rz5b4&U!8J%S&Y6VGXPrs4a=-Vg9=AD8>JvHUXT+pCHV*X=M`###R^zDMab;9J5YBo9MR;Q7+J9sWS~DeALj_U}n9exbPW>a#8CDZYOO+{1a@F9qk%u_n8n{ePYt_WpC%NSq!!WL<1SieMe9#ljCBB6Ve4tSIxfUOT^r`#oCnn7kS9bH2R@zhRIe{i;>LbAOG;@So+HB=h<j?^o?_-@vzY9U}4HWMF+G3$D%FcQTIC`IBAzzR9t2y=HEB-#5Fj_?hRbEh;zWH)jF*YbgsQ{>`tpx%hE^#W>fAwk0H9eDC&4CC<<$J6!z6)0W75e>{%&chSSdw|N}J^Z#eQxbK(UB)+l#Jp3&mzH|01-CM~yuQl*I=Im>F&~WLW_5k^G-wwaf!pYJvdJWzmKG+FA+Aw6FeUgm&IkOLb?na|TGtbYSzsLXEe$4cZu1{qg_6@_uH}maHP`-8TbbP-X<DKU0Yt1q+{w5VL-^u6U2bY;B+C6={i{Gs~#+h&f=jWvo>%=d;WwFfnN>032*<S{J-O`eOE$lb+FW5kQ{b90P*W%p^;~y{`{f+c-GXBd2l3e{kgT?=B0rF{2kmm!<95+n*E&LYy^!P^j!BwQ5wPL4nZVcOp=kL{Jk%yFb-#Po1EpL!FpW>qW-3-L>Y>B$<RBeZgUw4Ac*V<|a>c<j~?;)#R<9VQ%kuH9Z6XNT$@&3y4m;VJ9zvCr*Z_QC6&BYJekMGy*eO%(0d4nXrQM8haZ;4CA``!X|UE*u8oALf6$q(z>w46L=YrA}7vA=N6{O$izK=y^L_b<qE1%Eu3f9HkgmT5uwz2$rz@r?!Nk+-}72c3P}{B8JN{Mz@B#91~7zS~Re=Qa4<z_hNx_nhP#GEU<oynogEo`pYUE9yLdB;Jo+D!ftrpxd&3M*I%MY137Fz06(2FWdWovv2P_5BszDZH(v27vkGeo@4w+pWuC1yKU&7r!>x=_N(#!X6+gA|9K8%`u{u!%%VSwuN5wd_viZ$VEmD8n<Ss+QTU76;JwcLE1UjppJw|1ZJ&1a*erSY$2qB|_=#`*`8MX2E#CoWU++8`dHB=+u;{1t#kWNsmHC(*ZzKPWmZE?CU-4f3<MMd_H};<RcE75)AI-$?etOeVTg3mU0qVT<)f8v{pXaK+G#LFmK0^Jwe~RBds$__7-aUi*dGPT8XW!~Q3iG;g5$ia$<yP@;`C(ojYjEAd-No0<6q%R3W&+09c7phph1XCgRZ_4n1J{agq#DR`<(2TOZxP=dc?;`0>kjJS+avHN_{h98zXEu#R`Uw{zAG_bpFc3anXfUPJUO|47o*<Rm6rE^_Kh3y-fyDUL1$mvI1A%^l}F~Q4fezP!ic}H?v;}<&RR9#cYJ~SQ#A|5`CW7TzIr_o<G9}v^)`1L{H|9queP1gzw>s)DSrg}v8orwIpRl*r@$PXZ|S}8zVqZu@y)5Fa9*AEIe8?^<yU!aRfc<vxB7;nX?e7wTK_&yKglao{mayU|4IIf+W)Jc<m=R_`~Uq(KDT2Gxg0GoH6J-I*^^p?>`C^bdXv4#KGbq#A98tWRdRW9HAkyY4W?El2a{V<8<7`L2T>c52a&r|Ym&Q@+fgf%+mV}5E#zk82GnBY2ILylqU0LnKx!d!Ah{B?Fu4*rfLf3oK=!A4kp0Pij#iOcfa*amK-Q?)w5)%Mvr}`Bvy+RnDK1IPNiIn)Ma@GlMJ`RvO)gC?L(NMrL-wV5l6}c#sb1u=<SJAjausrQYI$;XatO5=IfUFq%c`>`Y>Gc}v^mu2)cWM<<Z0Ak@-*^nYHM<4UCw4xyqrz(8aBl%se{NX$>XTq$>Ye;)OO@(@^ET1@^JD%Y6J2>a#v~%a#wPDY9P5ixec`vxed7`HGtfb97^>khmu=R{m3oI&9$tWZqBB-siW!C3e<|^3grCM0_6N;H>yT<BfC?xlikTBsKv=8$hFuM2T@CsgUGe1rO36(b*ZJvb;<RpWytl&b*R4NI^>4bvgC&3#?&h0#^hGi>f~1Bw$u=ETXGj_6LJ@FAL>WsKI9=<)}9%{ra0EoR!|pG=a3hYXHln<XOU-8r;%rp7f@%Dl`bbQAg^LmyqUU&yqUb4P4PDBO7b>xJars7o;-;fO`b%aKpjq=KpsOKNFGCuqIM-mk%v*+lZTPNptd1@K@O+3B!`oGQbWl-$-Ss8$i2v)QJa%LBln;-CHEkA)3WwtH#WteI@;INxm2Azm;4pA0{JWQm(={^FUeD=ZsaLsgX&H;$Wy5$$WzHPsI|y5$T4h+J5qzl9myT2waFdGVbr?hF!IOLdgPDEovC%moync34auFzpHLf<KOy&~wj%c?51_Us4<HYwb|DWYkEHe?k0g(#4k3>wkEh0x$CFoUS$lppo8q;OwuNe=t{~gUanyz6IP!ezEb@HvJnBsHJn|Ci0<zLo<R#?wY>M|%H<S00_fvP1_mdB>Dc(cfM&3hCqQ;Yx$O+U*<OK3$>ICv+@<i$w@<j4jY7}`ac@%XRc@%jB^$YR{@=$6xc_=xO+LIhfj-d7;N09qdKO^@i_oMb8_apbEb|d#CTdALtt>n+OtTW|vHpPn_Z6|dH^=tAD@>c3x@>cQ&>R03q<aN|9$?M38)G6dd@<ysb-bmg~ol4$LPNvQvCzE$kW5~P6JK175KcyYXi^-o;J2>U11M{ae%qgE?%(v2yo$~)N*GFk*r}gU0^;FtP%UWN>5!6q#ta?x!N$ss=)sNz#)B##ny(u0+9js;5r{Yo6ky=(gD;`T7t!34};)&GpTGoD1Jej&$%i3Rx6R2yoto^7sNy|F3GWV}ywZ9Kg_ffZy_mMYIZRAblZ>VwPZ^+B2^U2G|OR4k7OUeJCE+H#jPxg1*2&*_+RcdW=RdOY2AX#Z4awYO(M;udw9-%7#2tO<Sming#R!#9?HpOoo?L9Sz8}v_d4*qRPs)|*T*AFC@B$r@QT%1jD5o&F65ppqV6>>3hQ8vY1RDZJ4f@CkUJ2gWCyOZCuWpHkXsfVZ;<U{0xY>Kb5DgKSBuJIc`E6&F2`jfMf^HQsl^OCbuE0HU44Hdt1sGCFYYiNp}Qgf13Q~cJUPaN%cP5b)`lHy#{x8%3%pNma#0XD@RR5!8*IUiMxDIY&8{>#yxQ-7ttB>zgjMZHhHMgEaZ@eS%z@(uD`>Ra+%@;&PB<a^|wsZYp1lkJZ76ZIGB6Y?+Q7gUwI7yPXFgNCL!KXaRloQt{3&!*UuO>rrz2e}m4o0^a8O)gATc`VG&iu1T-<yx_7ir+cfE9yh)bMiy-ZR)S&+vIE1TjXoxbn1`fbaE=2;&ap+<a6XS>Roag`6Bfm`6BrW^=I-G@@1->e3|@%(^~$(rue+0ouyu){zSe+zDfOse3Sfu`hxs`{EYg6{EYkuo8sK854HBWSp%Nr+~n$PitABJk?WD0QoYGd$vU+#Str+}<{{T5SEH&rsK(EV%e!UOiel9imvN|%8}v0lEB`f{;z!hn<VWN?)Z64c<g3(c<g4Th)O7L%@)>F>`3(6eo8s@N=g8lYk5kjg$I0JQFOt6}r%<nuQ^=>Om&vEer>H-WPmxbj&y!D*PdL@$2{y&YIG1Cb-!b}`^F7OaoMpXc=I0XgcZv0yna`Wd_f6JoX8s>=eIBr0GuP`G*Hh^qPV1}Khc%$M0#(&+1=etNa*(4nakN@&ikmrFD{3gU2|1M9l1*_#Y7n_0xu&C4r20{V$bRGiYAtdAxiXvLI@D(5I^-5kV{O5vxV57-rZ%FsA~zy8poWqgkn2-hlIxR$*%UXYHY7JEhfr&hL&!Cpa#4d#aXCjTP4%T#B>R#rR6nwXT-MRT+PY;cn*D$JznEtIGu+gFJO3X}|M{1$KZ7~{Wt=0{-#?0lwauY^ThOvO{-eGS^iglywf_RxGADZ'

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
