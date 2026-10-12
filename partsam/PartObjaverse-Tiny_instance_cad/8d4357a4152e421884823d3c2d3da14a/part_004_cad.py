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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8d4357a4152e421884823d3c2d3da14a/part_004.stl', 'relative_path': '8d4357a4152e421884823d3c2d3da14a/part_004.stl', 'source_sha256': '7dcb9f1d665c3584c07b6767f9385d158b8f22ddf716442eb83070d64c8e0c98', 'input_faces': 432, 'input_vertices': 292, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.3002808392047882, -0.4999588429927826, -0.09268073737621307], [-0.009825157932937145, -0.04973211884498596, 0.06573466956615448]]}
GEOMETRY_BASE85 = 'c$}qM33N@@*S|4G4G~c@k5EIXsIkUJP(xK})*{c4n1V>CMykCrN6Zp}kVg<HiI~NB(VEpzYUYWesG&&vuWJ48*}vb@o34Iqee3(Iwb%ab-`Qv1eb3qF+;d)*z)rdI_-Oc7No&z#bP-osO;b`x^U*#F4j(&gP;kV%qrxIRG%w-RKet}^QIF1neLS?!w5V!>gChooS8HOc)-0rPwOY1nA)~{`h7TAOG&+26u;SYd2#p9f`G}zd!h%h^`g`xcSIbtfMlIV!+yC)jK{Ey0sYc)LSGo9h*`>7J`Bak9_M;8Jr%c@;{LKY1N;`+Y2R^)p_}g23xIk&wqDtUDd?>tj=2e*RCw+w1^VZ%jy1?!6(!Q?<{F_bRqqOaE;%bTa;LmfycgZchk#P8HE3X$GmnrQ9zGyCd*(czC3EU@km%s$kJ%0qReJF9X?my|m&$@{CBlhf<_i_E0qO{}Sarl><yI1VT)8~oadlddN%5RZ8^>R+hE9hJBC8}?g_q?2i{Bs=yf8gaN;V)fYEPUf_;LG-u=i0rEWNDAx3V!}e$=|hffQ-L!VI%m#yO96ePkXmi`Bh0no*|BH66g0VsiM=9;9uaijI-8s_E6zdmxK3iwp(=3x)CalW9ee>k75vic8zrLzaNMAi?cJtt~pW0!5KRr{#AT8OM8!?&m_-jbHQhymG{y+eZD>if9KLpjDPDk>bcsesfb^?x8&)F{3}gtuSwvyotE*}uG|?WcB=@)Y5E89pZLAhq3z5N`1h-C$hc*nUMP8n4+bBbBJZU~kD4rc^QVa8lUL?T8+#)}-Y*|`{YZ5@w^#g3iIdg`e4S`{FYWfhSn+?=6a0yv<+++Oa*e$2<@Sj0TMPAH<<HUTeeL4|z&Dx=|FEko<-JF?6yAP*F!B$nxD<8M0`W_gm3nX_)LkX*ZR>zvc?5Z$@rjgrh^qyDSYgT2$QmN`>6}{=&n?$k)~{B3pUkJ@b`9{~*2BCzE=Ef|+^B{)WgcN2HMlEzx}quzZ-hTIkheGLtwKe_3E7Bz!X8WzzdyV<KA&K{r#6k0eqG29jh6V@gxxb_9#<3w|11;yH|d?FPA=yHfA%@*r{jh05<m3!vtn1hig8XjG(qy;{VVvMqcC3?T{cMkw)cfMCX`41>&_%vd2MqX#-Y^I^c?(>=h$cb{rx0<!`s5!gKlHKe7a(PAg|y08SA=Ff{ed5GYkBfAn~{V<(wvYT)GK9<Dk^D@nz3R@?7Hro;$uE>NEX^aPb>>4*vF!Fh0A^hUMS`FJS+CSa7a9XVYo$OZv+A*dhwdkvvx&J8NC<dd(GI%JVxM#rRZRen8r}FS+?Q_3Y;<>)o;Z2;wjO1NHnWc9GQE!b6C&y0XM^vJSO|2IAD|kNRA4Y^vy({op5Dk@~S6+A4Y4>h44Q@X>hg!2sF!ToW?EcMO;3+KP;j?}BUG4#fFE!~W2>ri`1t{C4mo2ElKkhvcId-weJ&3G7o{rpvyqd!{3P@9(f)3QduH!`?3q{N>dcw|aM{t9+b!Hh>Rmiv93uX<1)xUTb!Dqwt&Jr4EhkHSmuLka^T&+fHt2;kEuR#7|#$V4aL}2k^$4SQ$_IyOAkYUOR3_oR<Yw$ooB9iTFv`$n&>*vhM5)o!}q%VSE}#%X)V<NkW{~HmsLZla@*Rm_+d2LGUk}I7;&HUxxbkor-#n>L~k_;kShA?pZ48!j5_v7YDv$7x6cyHB7Sdx_u1xnS^$;g%4W*eol4NdB6SfSeNq=XH8Y)`D(4~tHy|V;A?&?^`l=nfahk!AkI%osGk?N1}lH9+cfa*b3&t?vadSte!=;T#yaXhNq9$t3E;UO+Fm|gY2~%#CCKwp)Bt(EYoEh^K`Qb*c4LY7`-9hZti*HcU5^w0b7SG}JqhFdKEBt^lB3|iry2IWxf8K(j~EGls}1k_X!<zGYu9k_jSYEUW9WL!OJVTF+)Y@g?tNz4Q23uXiTY^}CF?`W69Rtid3?wH4~oC`dJy<QAItdIW2RzX%??66%x^CBsb}H)s4wn|_j0YpIDArD>cVli5BTS85r0vTjHh#UZ}8mz?Yl$qovqXb`S0wE_$f_g++3L-z`xZMoR=1Q39lC>-y;j}^>Nag9DJuWsE4CZhf6(V1mxIPjqB6aO8fd&c;6rc`%Lv|2^g1_$fsDi<YV)FDC^F)vN`<QJj4Ef_;7-i*T+uB{N}$nD2M;XhTxlTl6}CQ*cAM#f|#$YFxdz6fF?QCofh_dx!4OD<ygOtz~b`0+O7KVf1Qneqv$%RXRT5#<nvi^%;R@$vCkZ>i8yb+gSwimhv(n}H)B7EIXF}0slO=A@9#$0_q3Kx<U4K;D4C<qwaw!{mhrk;6nwsenBRQ&aekXz1pIJ+)Jct5<76DZEQCA<e1-8zI_(g<>RaG_<1vprvqNPbkLJ%Y??%92IR`q1=Rtg*EIGH^pBA4l&)t_Be7P*tVavU^7d&}!M(hHABA=i0B%n^83$HyKgM7ZND(l_hdJO(a37mfleK|&+KmC#LMslXimp*&kS5l`F?<4;CvB*F0@i3LY>+^evGrOjo=e5I4aDTDg1^=Kxjykc8z778BzO7i_hh%@yi@CrbY61VH^@qs&2Hyl<<_PxTjg#d*;@WZz`9u$wea5-UCFdV!t}EdGY=?DM@|Dc5>-qPH(<2e<YkM=9NBgpK;H&n+`QhXvxesc0P9aXK9q?b{EAwJB2Cp@Lin>ZzACCUtg0J0N&W)}L$@pF$+>bcdtD=5R=auztdmFs=EFx#U4ciC*Ro&qKY%l7q*k1Ve&z5_cHuNFxJNYx=-|HgIC!N2+eJ$4x_<JnC`LHYQJ8$@jpJ87M>LlMC+lQOMFSwVAdCQjlL4TeBK64TFhsbxN-dsyJ;<-=1k@|5}Y%@#z7Ns$t)^ZN92Tzf8?Ra-Bc-=$h%Q#mD_u`4kh~I0z#CK&B#eQ{U1^lme!@6EnUB0J|QOn`~MM)WFqs($Srx;#K!SB3>@!S+MR_bkM0^%&cj=J&=_(F94MeslQ1oJz7tvuI}x&VA=s^sUK@wJ>M_0{vhKYoV&CuxYBpY4xh!5>(K^-?TgG3p}*eBe~c&mPel=e5{r;J24Ro`<j=-|&ea$h;bBQE#?-Q^8k`knfgrO{$!ujOa<=!zW>1^=L2WVf{ih_~)<jUQsQgrQhKw&euJRXAN)pzT1*Uz`w*&yjR0)8E3uSaQIjMN_fZ3S+Xvit%kzC+I`$N=JdlkA$|z_pI5{>dcFhe=za+JTE2MS4cDf~bLItOpYie(f8)vo+^231MEsJW*q6Qvl>37HOkc#=-W&Iq#2+!vRlvX5|5t=z9$$3=|8ZIH{4U!9!RtkC;C@v4oQ%KzTL->xH`$l$P1nnK+dGlxxl8MceeVt5B^3KW3hs$od>ioXa?8GEOWle4>`wvUGc&Po$DYOh{9a4s`BNY4t1arwI<-YN!}x6T#(DMFIUV^mMV!vvrJnV}hbPMWj;xP3<NM%uC%<_4Ubu?Z1s@S2-#dGS4f5Tz?WhC(_#k|Dj&#L5ruiX0e?KucpTqqkxf*z%@z_tM#Gp==_#zI^bxy7$XIv%Z&-0s6ZmHC>OD_%oj-~OwUKIl+&iPV^A2|l|ZXaP&<Lrtm34i|nptl|_zi+sC_dQW-GbdR2JCFNte|v`c>R4XxYpzWN!8aMrajPrmPe&im9P_AE?JK`88NcQR-|Up|&YGSwo_bpk@S8q@|M3SSB>v^sr-cuhh2P(PdlZ|4Z?qhF#w{5s@kai78tb75-s^06>~HHHg7+JXy1oCi?9W=eyWnSpVjt_>!C&gI`W3`4;llZUWV<-j!Nt=#>aEIH+@mY}0G_{N*r%<O_^!IU!MpD-$1lkH+GpOvyyo)1DSkVCO_zDem?6Azspbu7Pd*{MvvDfM%hvt6=o9DGD&7_mh5UAH1K;f02I1R3z&*dFUE&+BzRys+w)md#F4s)qwWZ$)Z`iKjo)Fqbo@;NkR(My%IPje}Ab#oXl8>JJNWMcxfqfFk(c>57Z~qCu3y+N!-qyO%M&So{$M^f4EQ#Z2b0J0YY2HS7+n(uo-`?6fiGQU9zC%g*Z|2}Hh01wI4|)Xu#0klgfAN9BJJxSR{AG_<iU0okTmCIiecw8qQ$M-_zQ%7dZmxP^!W*8yOB^kxy1b9`%e7dy?>xeMoh&8!yLqkn9q=5VH~jvCH*<{Ve+J5TOWTh4#?P4&-_6^eloQ^@=W2`k3GaBh@~Zgz;P)uKl%MRQj=HsE9Bh0qBREpNhpt{XkWbn7Q>?sp3iab4?;5Ac_t??xwfO7)UFBTl=3R3<u1UXo;Pr<O<Q!x8@05JB%N=lDin)V(e)c8IdklUz)-FbZUyy-$bk95af7XL*>U8X*MQ&r<4&Glb`R{)!-)H??3gU2n-TXi2-E|{e_E+b$4U)eR_pQ`{D{3V6-ItvAAI7Jlu7?Wm3XZ}!v|WSy!GvWzr`(lsHh$0AYUS;-`(3y4wr%t9`+YjrwJm>1)PL95<bPWij@%>Q-?Y8tX+Mj<r`TIKgm--OC-UhzPrl>&z>{)6wjaBX@d>XV-_pW6=4Bwx81UL#cjWgK*SX`^2WB;v@p45Lm;0hVBL?v~4sPDI=sy@Y@><uuiT_sTdbO*|{;kf9OS^=((cgG+M)G&~WC;Jy{l^x5LcWvs2CJ~o3=G0~EzJPmIuGI(Z;AUzyMFl2KRge9$zO5uzNI?FTi3OV`=LE)k9;TX0}|n%f_sW?^pySBy+63P-x__N$#=#%J011*?j_l8HNR%l#Xi{#`HxvA&ov&blJB8y@?gZ-`AGa74J*pI%(nW_jW_;*IsQ60%j>sRhL2j>n&zqbXdweEe;PFC=hpxJr@>+M|5tw+tY7c{{ine^9-8)-na3+r@)IlWKc;?e%5SFRHtj!6ozK*zO(|?j5mPGCE@{f!v=z=r|GcIyWlA|yikad?TVd7qS_4+v%i`lnKgD~JE6@1qIW|)&)2?KSFKy*poPCw{Ay&GAh4&<<bU|XJ-y&AJEO8lA3Yk*E6mL_Cnxc^_K;FZYKQ!>an=0Fsm!{<6GhTBXf7LK9YFuBC`^A(eraU#}ktz30`Pr18O!<-a15+NFa>tZ=rrafdNc#@Cd*mK7<}*{ynR3vS3#MG7t?*G|H+PhN$B7kxk+vHveTDia@lDzn=zEd;x3t|@>3!7S6Ms+pk|mbH8`wwrtfcM6N-w3}OuU))H<q{xFJvF(GmEwxD?N>RHt}rQ%Pnygp36SUXF6>+R(dRTByl8d-4a*f`Rt>7CeU_crMpx2C+<%>*b-OaX!cP)AJTSXrE5~ZNBkb`c9ysbcVQppQ;oJ8D_xA*huDX<uO+T8bvt4o>ipCVO{r^2Y1(z^+mN;|+mwH9Y7gRKw3Xx`uW)hNrHS)f@^iOWG^L~|O^J&WEB!8YNyc&8b*W1ePhy{UiIwg|U6)wtR>bqDTM)<4?nIv^#7*cE!?=puMcdtP7u(WJNv3_6w!*7S*+QI5dlzL3`yQq}kL}8@19duaZ?-A?Hth}+<<rrWB5dnGtaKsjj>NgBHO`ZjD@<PDK-wORRfsVHiMN`viFP{eK>DN;2h!&wVx_$qH;`Cyor#q$WAX83K8njnTS;E>-sF{C!;})V%h1k8DM}xO3({7;rO1^c?`~IiW#Y>8SGtM?2hdi&wa9&Jik-L??aJf=h`%&tJZ(Ge0CHat2N3rmR=P2t7eK7I(H6cjb8Ad~fW`KsC>%sRfOr7?BZwo&D{dlfrK5<I9z`5MJe+tO`;MbMoYKIQP*ds=4`;s*h{sWXMXsKuZz%Z&<V#V1Kpe`pc;a~aEB&=8hfG;O98XE1PYP}26GFdu#tR`{KwN{m0kPtf*!OGNhZs}owbUnxmG35Uhlo#76#kC*JNhebtHoA&8MWFk<`JjUcDK!AzjRAq)i#uR9<hUMLn(@HL0;KisTJ4UV)vsAC9kBMDK`3+BiEL?jwzr1gR_zENBdKXYX8KPL9_>((t~&q?N8~`mHj`ZPgmml#65_6u&<XX)yY+*U7uW63$Ju*io(4p^%<u%?a!zO5hs{3hB%J48!H`4{ka7XqCJLj6*rQ$JKjjP%`s&d?M1ZRcqIK*`}?$&G-BWPi4|9#*v*xv&s(Mxpk0Y}d2(JBzC8PuCtsDgswGY(&Tk!J<*zZ8`#Bo>t9r>r-bVW^a+-yIi}Bh}zfY|62<l<PBRD=Y$;~163HvA<M%#^*o<cp7IGk-$$gL)x!L}(B#V;nW>?PETiPxFpBvz70E|#{FzAI?2pwANe%phK4%0{-Wpq)rAm00N=#7ffmtVHr@^w~*U$thEg5TBu)M*9eT4cZ2Mc91_!+n{}hqIeha4O6nH&yYVwoJIS##m7agxLd?o#Mjw3i@9ZyJ3_5|&Jv#`uekHHmEKEymUuU@(i!Zd?ERFp<W+kDvC?tG8N{*l&)}G6kaJpWC*$uYx0^Yrc*jiHM*BSNz2xQ)?<HPDyoi0b(SJ4Dw-MhWuj2hc?B<lchknZ5PB~`bmA!&`53%ZZm9~-t8fx$=v729`{avSf=yQO6C#WwIU#9J%{(*VkrhUuOcH7d&MVx7ge}XuZcqjE~?eCgB!M>T~Hc}K;>m!Zxq~>Tb$3ne}TK6+JuQNH;s!e^HK4H82TNO?&jQDfvSmHsn-TRvIReRz)8oo=_iPiThFR>SKQQArz^iiCjg%4tzAF<*z_E&M*^4aRSYTxzLu<xpSPX%%<XqO}BY4KHeKXpGSM(jzS+QdqiCHACmE^@`lDeO<XHnE#i_gr<y?Mv)WsYd^1v{k=>^z$b_khmM|+Qb8CtNZy7ay@CgvC{3?KG0$--ICIcG27E_LS36!-8UPuy%lXYZcm?fd|rF{wzE7}=d*)}hp;`Eebl>7<+uzaR-F1BWIgT4v=t8Q<dMrK_y6=?BmVxUt4Yf7A0__TGw08y)}9s2!g%u|YG9|l>ON&ocrH1}lvX34{TGk>5AX'

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
