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

PART_NAME = 'part_021'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/66e6c396a23a446ebb0973de52181e94/part_021.stl', 'relative_path': '66e6c396a23a446ebb0973de52181e94/part_021.stl', 'source_sha256': 'f81b48df9faae9f55b725c5028ce5688237b5ac0e93b83c83461909cc16d98af', 'input_faces': 349, 'input_vertices': 244, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.19189324975013733, 0.12539324164390564, 0.10770343244075775], [-0.06417141854763031, 0.27938467264175415, 0.2467128336429596]]}
GEOMETRY_BASE85 = 'c$}r02T)a4yM{Ls>^)ep9%BI;iYRJq+ZH7XqFAsW6tF9zv4CaUMU52`7151G#S%N%VOy{u*kdop8jQi%lIYle*7v^t@xOEL%$<92*1Qid>wIhNwZ2u(9s}Arf8na(r-C-u=RktJgr=#IUvt&Qghq@W)IW5T=kW0HPFi8{)z2qg;@`zDpu3YcMvHO}2_4lx!u@NTd*iSM?lo-gVIv|&M+6V=J0c<^RQcZo4;>Yn?T;E593GneyGNb6b!*tXtJbhhwEZ7{@@98I|8v2~lx(%O%|F{r{XR14uu@~Wzxet}uQTF%)wYysecOxg7_#-W)cbj3ic;%s0o32t|D4o&{nruE_b*RK{kTI%C5~VJbfsqG4e|9QZKb}^&6N1&vsCyM)1;n$=;|TSq@&_%uewV=tvvgZrGCvA@$DVL(QfB1633PmiFSY7f#;grN$MMS!o;^y&PsiKe_`pT{l@^bJH1A#)aw^=OyYml9&r}5kl(H7K>52?tO5L2C60?9++Lo~3iT4-yc;fY^`Oo29JUD_h@Ue?>KX0J;d9NaAkO(580Vr-4odx7PU73H>`4>9@?Gh_KJfi<@eetlmwKJzWxg!;2jbhUDCwtuJS{`oxt0XK%L<9F`CpXymc9XT{PJNO?)Ag?99t*8<`s>3saVGP+_&<iz|Zu=c*Gm<r+G;~Y{`k3-|dlzbF9ZHslRxN<cZmRF!~dGNXEwz)LzEHvBNID-e-m6m2Tyec{c(B#Wz=HN*sObSj>A?Tf|xZQsS5moaOn9tM&0*yXs*+Tr*|9Y?0LvC$fl)o4KeF#;utL{8eSd*Lrlo{0uFQ{_lyC=eJ*5BJ-d%F9`qj4tai~p@*neFb~Edpa$Z)^*<@?T+E61OWR8xIxhMkpTj<;N}N)^OFgZdhIRDy-|(BJVZDqkh<rQ#LVR05A9-HeHzvj{7kq2ybZOUKeDVqD*W71_bM6bt1FJv<nRmziN8;;mmr7jgiVvQ5%pKHU)J4YGoLND}Su1$~{u)1ders!M^uOmGv}^ez4_784-#vDUZ@+#W`$+HN=#P<rINQRI_me!NzTvl4e6ug|ReSRGfc$;+RQQvYBTmQT@^{;Y$!Iq?7X2Jzm;P7{$BFNlI0gI2%tw+(+Qi;?-nfR+4|7USiDzoP5P!l$tp9S~O25n*I{H6oHrieD2A^wE4gLRNm*koGs<(`%?(Bj1?fXf)R@OY}m*Zq*^fSXl##wLkgM7}GmJhzCuZ)}Ba!31Ja-ly>+^}zUb(3~&Q~x|B^>0Qa&;DqQb?5q2eEYOlvL5Z<yP%yiPvE~=g7s3OjEs*X>bCe=kNPr?2KO25%pv$yYh%1d_7&f3ycu!s&6fPIxgC-IJ5H<@-`E|BeX>Oa^2dFJ_<Hy-83%n+Ma);$kLdr~mh!yThst=4eDlP&d7Q!chONLlt1u1mo3)a4VH>s(`^Nb3=+E_znD<U`$ir(x#dq`zk$uOyogw+7XNKXq3hT(XvK^3bqxzwrb(czfW7yx4=hneK=;yusn8#;%WIU|XLGb54!#Z8k0ri&!qW?vkVxE5Pk9-;Kg?{GWjQuCFJH}~yZSl>GAsC0sA@X<oyvlgqYIdyCQH!Pj=F4KJ-?ISrw`#Lx{4IAU^uNws?5mUK$~f4n{(4l}O)et+v^)2*KKE_QR!O`1o0}5PI&cTRtv1dD&$}46q3Pmlp1H7}FW!lG_madnpESh2y}l^sEms2KOzkQC(cUJ@_&EBm65rae3-j1HL*~&jd>Q<!Ez!S^^>EI+4M+c1TexQodn)5$_v;S-L=o&)`)<g%nY|mLKXrFvf3K7m_ku;0#5W=;;CbC+@VRXz5$Bmr;yd01;#{@6pg*&IlHbkAFC_nsjZWh0V{1$PXgMP=ZZF;+5x?L(>}%ehnD^i(;u|X#VE?)EN}fv_lqtTsw-45P>Kd%yeRokmKDYdC_pgC_%HT7I|MNEFN&E-oQPbn%Yx8m;?(#BNzmH?Zx9Sx_{y3)~f9A|b{r!uu56s-3jQO04`oGMQd9msg$9gS03+;NGM!T{8(ylf!Qhdk4u~<L8Z?TV+2uJ+3Ss7UG_oQ88V%x*wpZCOh+9(D2Kd*)O_NJ~_k0BK?UnQD~Z+b^!zG~mbx!S4*{E;W%_x8rV;Z{j}J^U{GLc@5kEF`}5aH!OCl<X<-?awnTsbBK~_SuN~;+wUmif^U`<Gj8$AM0yWNQ%U{d|Tohg#)qw&FLw==JOH#=s5uGTxue|qyAph&y@%F#-PTipRYXbb!Uenul5xa-`;gK`d{=n#F_P1viSA9Fg{@q(BD;A;%m1%U_1lP$#~kIrHik7x5W5o*>S#``@}cAi(|ivxrO$RZ$kZ#i;%ZY33%?Hwc?v)hD*CfiSKYvDf~U+<k}!{^d3WT4~&@$e@GkTVdhEPSA8alZ%ev^d^^=Z*1Og@0`cqY#=X=xM&fJ7T8nQL$SwP<ZBUHtWA?{B;ydyeMgE-(Mt|P_a8T-x#k^<-JTUK#+lg;{h~_xEAWpcC`1<C{sNen)&Z!$$4@mteU)-yn9mD!tas<AsDfJx*G4R(Mgr9l|_i64A_5+jQdriiCy={*81^S9_H7+9KV6U?c`%T5JsK3?^dGhCIY2T6FT6}%2H}<2F4`tkJ`$~zgoxX^1zBT~+{DoWlB~LQ)VP1~D#J$f<7GJAh7x_A}Bi2_^qWIPk2l8zC1gwjo1o-2ZVt-rE`YhJz67kK2O(ed<c?a&*Swj)u=?Ko>N>^n(O#g4-*ByuNgA;=AJ;l46_y*UnR%Ac+kGt#kiGQUX@*p}(o=bZ<1is%vtc#tkaXwD_xL5l5b|KnzIgInUqXT~NPBLx|1LuijZHoB1IUoCN<@d;w{Ym26)-S>Rt@1YH$<uh$4>oa*Z2A&;QEiU+_CbkQ7Y#OIT!)Pi-*|c-_lJdDa86e4j`%Ca;(3>r$9Yk*I{G>AS6O%3x@9=epXL_deEbgID?Z(G*1y;z<LTBK{lD`7d06ea`2W5q|8^Yt5WYry$4l(j=BcgN$4d7RUw>Cb?uS-+U!1=kd=aP62#oXWIk<2B))e)<iovfn0eSVj5&F~Y9{LgVC+-Vx8lc^a7jX~a{mp1uTKrGvz802_edbJY#M#jX_s_VFsPFMINycsUOpJ5C<TIc9ju#6h|Bd`J@cp#cZSi%z7uxlFkMpZ}lKA${@%Vnad^PS7m$st5u>s?p=!yKfmw@`qZCFQcRWWXEcJZyQameSg6I0Ni9*A>$CE6|67W?j&An}cQfmqjn6~=je-WTyFBL9rnb7cPY4eqF)F%|1=d}WERe{B<ATjPxT(xoTJpXoW!?qetUyrX+2_QlvYi4w>68SX97RWP3I9>L#V4C6VxI`aA51@Y~PC-A(riecXKWr(l!;roP)gEC*b|4#9(-Bqyv&Im+5=Y@%Hw&Xg=9VqSS<@<{7$c&KjcVzBFf8I3|U%#3n{dSali*YFBiTGiU@ZRRH*F1+^(f{at$ip#zVf|M6d$+{*c!a#l=z{U7{z`mXmG}7mQo14L_x>&Mjk0ScZ*5hQF<%32if?(Zz&W0`Bl<JuviRDHPSPK<)CJ^Kn`wx@pc~eE{c4!soP!a+%2w=y=NqGbLNE9qY9W59G{kqWhIZ4NNd8z31K*bqmq-0~xEC3Rm!qH8@9mOyr!B<3(bWg%XXtJ5wGY#<uC?o!$AO!~w=N&Ve!eaW_ufZi#n+cq!SB&=CqDOWsSEJ^B}XZ=`+hj$$Iih$?D!XW?%9J;Kf)jTKq~|H_Vs-bzuOhu^O~+jK6v#&oPb!IH-WP-zg^pjZy)ytdAMf`*2iLR@f}G9e)m0tahjA{d}G#2oJU{c-eKIiyHlQb%O2E^?~V2Ca#4KSzK6)0-`69K*J1JP0SUN&-;6o=xo_EK;rnw`eZ=pxO?+cZ0P<&geSE*^GzImeZebs|unOxj?-11g_BGC}on4TRLt2Ti?e;@H80FGF_sx1y7~e&EFy5<cq5jOHxL5Svg!f@>%cK9Eu{fvB8t8xg+a2P!NkE=Be}z1%`$~MnXFKwt(*VqS${*tE=U(AH;1iAeTKG-WcYBWKO?5*5<I=>p_BrJ9_Qn_R9;oe1#A$mAdG&EH_Vw>Zqkaz;oY#xf5dT$k^z&gIoYz4=VE(_Uu;cURHTnKTi%s7y^SC7){q`J<=N&R0{?QxQ2V89Ud-O2zjUn$bFCV(4HVgQVxAVOc!-n51tZAy`(Ok8#;Ll#oD^vY^(*OR|{Ghu3t5@^hbsPSFU(Hv}?t@!)sZK3Ju1>C#UDR_n%`P>lb;xyCrv{7S($pekr8&q-bCOGwtFkCA%%V6K)rp*o>_XMZF66vaXL4S$jaq_iBe$Y9A-5ujQ2UTW$l=uC<ZyB%bpkn(JeRtFJeRzRx}L1`IC&L$FN@+->IHHt`84$!`84@3HG_PZyn#jW4(dtr4ssIp5IKpwj=GzybQ^gcIga`>IgY%NMe!QyPO{Ri<Td1<s43*1$Oot=$Op*j)U#xz*U9PRhtzvyr7y`3$(hs_<V^Bo7RAr0e~^_vB|j%WqyA3LqCTSjPF8x8{D}Mubr1O$aw7FdveF;OiR7g$iVf-{veFS`gFK2waVWJnIh5R-+K}9wT$cJJS?L#Kr3J}l$zIfwWG`|{syDeMxgE6vxgEIywIaCz*@x;u_8~W-dXgKF>rvgw^~mL@rN~MPk;{>*Q1g?kkiVklBP%UHR$7hx6}d5s;ub85eW|s`zGOdYU9!^FWIu8s^&7I%Z^?n=?ktLfsO`x?<WAH!WTj2XN}G{8k#%YfveMFIrB%r~xovg{pw^~VCD$gqQVWw^$$6-`$a%=QsV?N)<f7EPWTiH8QF2XcD{@V82NuO))DW`LaB>)VB#Yv4)JXC;ax`@=Ihq_xT}4*9mmEvp#G=@urjjl4QR->(QSyH3Ve)?RYU&2^YVtf5#fzvr$cxC!s7Yj{>&Qyu$jitJsVm6~$@5thFQ%>`EB%SQnEXA9;&|!-ay<DUi{kUtbh6Ti<n!c<)J*b4@>S|%@>TLB7RA3(pOck7BY!#req~YoTXuOseL~G5KOsA)kH`-4IqEOubL8#RM6%MQ<n81b7RA%423hGS@^{%~W_B4(olc(4I-^+>52c2Zhmt!|o0FB6B`ftJcO>_uwj}qb_Mo;TD{V*aLGH_<xGS{*S*Z_MX(Mu1ayJ&m{?vM8rRB&<tB{p`MONCFth5E$pWKT@aWK`F98B&<^&=|{BrEMs?nfTXqIeKBh^({|c@Wu7)yYcRlI`RH+CTg902ajqv&%4Q7is{x3%NeEHn~2z64jNgG!MBFxfqM$;?&&a;^gwwqU7@Auc<Z3Uz0miJCHk*hfu@FL&y=-k>m*S80t9k81gJ?G<g<zIW?BNoV=F0iM*D)nQD<YlXp>%l6R3eQumWLl2=eylUI;uQ|FOqlgG0to=9Cpo=BcbT}GZto<Utmo<W{Qoll-do<dzro<g2X{hmCT9F<+hQs+>=Co7F7&mo)CgJhGOOg&FldXbz=K0>`pR(gr7G>v?OypKikF&4#VsF%oR$d{?Vk}s3*P=6!eA>U<Dd|UhHoKSp&dW-sie2aXa`h<L+e1+;DUm>5Oo+F<kZ=r4{D~%y<At$gXUP7HtRyva$(9S7`tMmW#-xmM*G2{#V=l_ZEzkc#RU#Wcl$yM30{{4a_pq-0)XQ1WC{-+jhqPqQS{{raex#0'

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
