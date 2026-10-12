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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/63695230beb44ae68650bdd4d914917f/part_004.stl', 'relative_path': '63695230beb44ae68650bdd4d914917f/part_004.stl', 'source_sha256': '5068c1322e15094376b4721bc7d4f2e86e70a21cb7ea5111d663ebc6e66977e6', 'input_faces': 336, 'input_vertices': 239, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2400992214679718, 0.19806480407714844, -0.25834304094314575], [0.016738541424274445, 0.49757450819015503, 0.10833390802145004]]}
GEOMETRY_BASE85 = 'c$}r033N^O+QxTcmQYHX)_BY@bRdm+*fmyBLDbOZIziCZ6e5w3WQ)X5LrctrLqtLlAqXM1n9@u&7Ev6nA?Dt44ehOd=l{G<?mfQseQSN|yViQw^V?6}^Zutj{P$jb`;;nOU6X(Hw1N@UwiLgmX)4^c>RL$Pl;AH%1x|f$;^Z(FtqOeguSDZM9o)}%n2Q#o&1f<@aO$WjP1;+UbR5&RNefGpF_WeQPYIYfV$zh+fy(b0Fn(&F!=E}XU~-`2*sGOyyA~GjrY$THmjCC!ijFSmOEU|PIMhtLce#tweQA5uvE}*me5J<X`S5KWLUyTR>)q5m<ma|8QoiL{t=;O_?llL#?q)~6ab;sF@{(G?*RD2#uPvOj1$kdI&xJlJlKchRwjuvk@%PAguPga(k8Nnz(-7Zn6@0y3x6SD1qk-_voGa3Q_d!YUtJAMCTI&BiU?coXwj9(+ep~zvYgRb>`hysZ%UsrT2gV;cO7gGANPm7F9gp#L9|qs3>y3P)LtnIOZ`c^V+2L2Izr=GB@?86#f<{SwqjCV|!J2pdB-+hBE$ud&o(zB4RQTq@wc=m%Nr3O${{;GT`KZ+KZo3|NJvxj3j$QIYlQ3_#o3+K?Tki_|xf@VNkIy@X{+#lMZ}dyvfV|JbvZ3SFiQntlO3cp}zK7tCa=ngu@SeXG_1ZqpM7>uHuEB3SAwjA2={fjjqxSGE&)pMc{ZEVU`Nvh{dF_C2ZvO_pF|{Xr%WjXYXunCc)bAE4`EQLDKYfDaZ=EXbdg_VtcMr*rc1OO=J$5_t-AYTocNp?*73*!m@6NtFh;dC?1K)mh|7QGs#y$A@@B5_x<5z4#KM!4mZ=QPg6OIpb+==ti@4VDWI}G30zkCPk?OY{wR<A%E<FKprvuKp~zOCWwiO*zQf7FI=eC~rfTCd7!(C&{8pxtwe;oBaE!Z%M}hOha2EcJVp-iCVR_QBWPN6C0oCnlpm9y29>@|W<fU27*H-~G1?w0pRr^#5-9Zj3wS41DbuAE`fZXA0UavqF3i59xo|Y>d|!unfLg^^UBU>y}jbw?<0+Dp@$Mw7M1dpiYjz<X5uDe0nW|uZ6di{2O(o-Kf=AM{{f1ezbeAy!fS}(I0(slK2nz$+`y(l=;aBg>S~l`DP4DKtIj<jo=$Euff;uZQ6yuKR>(=b>dpWw-5U;9ra_j!Z%O!ME~`aa(nT+UBU2;k*DF?{QrQjhkPY<-pQ4DutZ7yhu-k@KjW^-ydA_mYg_K&zH44hmi!-{W8U<PYw(Q+6Q%z{7RmhV-6einKk5I%&(TkNj{#CAdY$Bl6-xcNo#AV?jdFd3Hi2*Yd5ZtQz;&%(y}4B#+n1M?I+b5wUG#R<_96e){&ciEJW<v$^3;C(U7rbGuNjUy=HaJupQ$`p{O3{9&sk|`*NCkH-?Vv&A9@z^X8H5Z9{65Ca-SL7ZyoxVXTmpTjF9=iX3apIgl*z)7$)=ij*pCMPNMkv%cVbWC*l6DyTnU<|8sIbyzmTlw8it_YZtdj{>BjW-|&kR|JWe-#_x%7@RLSJefQzg|0><FF1l;OJ<juBWOq$e$F`zM((e7XGOq3Mu{eI<BK22qko+@$TdR((F|Y7k)jj-V9Xt1z^J>p?_{Mi#u`ZUYmt`LAo|F7}(yr$5d?D)R7c&2*+$Wcx3_^dJ9o_9bKf3!oJg2nm!{TS9qrSbS1@*1_x5GCdu9SX8Z~G3%S>H;2&bLy3;WdBMOOJ%_xUl4YQZ5$fiLo+F`uQ~FwfVGeogn!ez81gY2?O=le<AJaEoEGP)<^#>Te?X8?~SG1tqI|By?9H0m%rrvY?6Bb_1agK{OX-BpJt=KaJ|_2x=Q|?JZblZ-x}mqdy$55ZEhp&T4!~`@#Tl`_2yZ!E;UNc#X6KZ0AGtaA^F2o7Nf2iFLfR#N<W(=Mq^$RR!M#fS$8eF0iNU54$CD!VVC%UpG-r0IfnSzZsI@uH3H-4I$i3-`-%T)>|~6~_LcOrgPZhoV+6*l`Lq*1bFz%L(MjwRv|;tcznm`j)fZ2`K|gP~!#B&{l;=@|F4xPrJJ=7JR}!S%ec?gq&(pKwub+<jx1Pw%#JY4!5I@~p=6`1)?k8Ht8u<EzJb4}siC&6!Jr=<?Y6i)3`I4~$e}5$VP%ZdJxlbn4*nsiIPL=vyFG+t+=1)+^_LXC${#>4K{Zg=>G5;}4>hQj28cXKm?~@1Yay}olp=KcZ-=ekjXXSfxpNYGR^VwRjk>qoqW1YERJ$~1;{I1u|hu=0WMSq64h+q3Q=Eo8+0rO)Yd;<GrJ-h?*ZT11nP_I^|?4wKe8(aRw{M&t&!q@H&lyNP2A?Izzc*!4kQT$pt-{AOmp!n5z{rX2?-)r|6A?;@8OF!KULohyj1*u=lMf#%!$D_Z~%S!&vy7GK12**6wZf5O7{s+Uq$M4hToyK*Vk`CV-5+LjNq6YR?#<UUQ?+9bN+n3{b^HA~E43d4$I}K%i9(YOpm<U;~@tbj;Xa)bkK3y;Ut33C2Sh0^Xn-z;6QYiH^u0)~#**AB*c762>!+CDYoCjZfI$ZjhCi_o&?x&LP^POB5>z-gAWn8Yl<F)fmyB~q}ii@_xpLJZWmz#wL(QeNI`1<YflAksd>#I*Y3190c`x*UsKiN;_B*8Da|L9RomLad|bn%aWC4O20?!!j2{^GZmaT!5%<{^J?Tnc<Ii}Zg&yzD1G{|vtQ$A@wq<wc^O`s^oo57S@1Fa11qX#tL#?UVPja9$U$QpdqRJsrN$`xmMI^9{N0t(XX3yBU&?c|4x_gF3by{7mXs;JQTT<Gx`G93=JqcpgrF(hL2n{R;aLBe%8qEzZQ?c=mAkrVH;s6=zLCdkv1_{i)=6t+~t%MSGWei~ne`+=ovF$2$8Z^QH~D9Vz4f3GZ`8skGPLYm6FM;`b^nK>w@(GA`4AuPvGk-_q~^d~@$4_<Dk;%+I05IIr}Xfl{ZqqO?2b6ZGFUrknV#&EQ+FYVw}7CkO9~MqNJdVjqX&`l^}<UyG9anAZC3aroW*7|D<3b0_jP*2}ydBKiH3u`b3WH(aM$w3ql{a(?O;cQ1h2Ye=2lvwpxjPU(y91=_m5u&*)RlIzj%{wNmLQSJ-)X1hi5-n3{L-Y-ngNcj4AdA?}2_5D$=ad+{v4$D5O{QW>2SFNA;+We<jq|QZ8@t;1B`CpKTc{bwyiSGeM$L7**_gV5j@^UDAy^`ElwagxP{%S+|NPg(A7?)*N48~>M)<W_%c^+viONXMJwFUAXpK|9k@)L{jeME1S3tz8R4Zf}6F8Q7kn<Du;Crh187YrHS9P!6>7JtoSycgJA+hTvJrD`&tH|~6kzrXoPp3kZ7sBb+|B=z;@;xB(D{)zYk^y7v<d}Bw?Gw{Et2;VGnfv@jg0N-*vBH!6JGup}d89r<g`qQs6z6a>;RnMYMm+|<HW2>KweM-smSL^lWLj1jl8+?6Xcd0)s8tqyNld*p{T9uRj<o*obIO{Kdelh0XI;$qu(elB5JjaZ&fzs~rVEL{zG7$d1o+CjGSITu+a~1ltWfbb$eW#$leRo;-=D1Gha2}WSmG432p5eJ?X4Zjkji`_BP_~dmc>d@|H=$koxm>hs+=|A1x8(kBHXnffhS9RT+>htV^Fr(4CH_k{>}U1fYova9tbDg>T1I?6r?jviu}{#8*JEFx*Ex*-+n$t_`58ZV33QgXjO$gBtZ#7{_-5;|=aKKzM!qYx$j5zGJ5~|C`Rt{9pSt6@2)a35#x?w&j4P)T-Vco0Kgj$PT#$a&S~eeQFDK*m8-x3vHh(ytC;EyEsefy>v>W<xF7hvbjXLI)&6rQk`=3$hr<pGKBkRj|w6WX7&z*At{XcSFzE5>O9SMKf8TiIecaBRxitt=Dnx>+@Wlk-r|HxwobU-l1Wx3S`=d(83g8O30^Ug9M0QU{;_i5M<YMt^?-yC#M+CAH547B5YS+5<NWFCB*50LYJ5BjfN|3Lb$)p*ib`48ryj=lCoe5cclcgrEK=XmMoN8!@X50?+cc*=fs5%q2H@_p?$@2@fMCtQC-eu}U3r@x;(53hM&f?xl-Df4?M82-3o<Qvy#9+Ua8%)s$kEBa||enk2?aP~~}r{=rz9Wt&<7W}{B<h^0<UeqzW$#+2Q?`910ew+kfyM2lNZ+O4aDtgGeOlm9R4H!5N$L*sqE?el>qnP*N21`&k{G80s*geON_`dd){7u)=UG*xCp*y02R$Utt;Pi=Hnd)DO{?DJtzx?q3^oiWtyY+wiiM+L=4<9+A2lX>@5AraE;_>Qqq=r&wl9y8#Q)iNAGH)?M@f_-BWTgYibI9S;zmb)GLJlWSWGL=M?MhbKmfVZnhWY`y4f%a)bF$JV<oC&qsrAW?$qlG=$VzLG8<1-<6u(WaL00+>`E9Z%wKmz4Y@yaAD{Vwp>P2qqh!&1$>4*=h?WjIvrJc!2yO7(FyHh)p`%y<YViGl!p?CnbJGnc5t9TgKyNCAgb4YO~YDek-@&Nv}BSUd}hGK835BWXnyHp>t56Ap2wFS8a=jdHVQ_h_ixnvF-l0B*Qs13;tnOBdYxEZx2xf!{Y(|WX`wj;M9cc6ABcOZZ4v<4qjN02`zf5}iB?X*tO)KGHCwW_#`Bg#9X97Ay>Y8kSMHylyb5!I+348_$MimOoHAiu%iS79i2qn07NkzJ{!$Qsp!T8dnXc`gjarK#n}rO9Qf704B-?$iq83e0n7D6UMcM6SfKRc0uD(`jDbq<WB*zC|u_#C1npq+TW~y+Braj(m|^NWDN-nn%v1o}}iHk5IFyd1R%>$Vv~Bv&eg?$H+=E$eXAM)C}@&>LF?dIfK7HL_JPEM9!feBOhb`6rZM^r{<CKIR5k0OXTz9pQsne7dXF)?bI98%jC;kj~mpV$v4QisMpDNsJ9u4Z&I(5Z<4Q2i^xS>*DDOgXQ_qcv*hoc*7$qsN%HsPqYTCSoz{LoHH*BTyq&t2yq&z-X^mG?6UeK{vl)uFIj#LR>LKzr@(F4V`2_il(;A<lo+qCnU#0#;zDoYZX)S-D-XQ-%E~efh7nAQft=~QBZL-q4WTg+uO7D}4sSl|4$@iJ}fcl7h$`Pg`4mcvv5y6g#azre3DK(C~g1U|xM^+k7R=S?Nj+{u1Co4@RZ>6SElgTRfv2O>+>C{wmD)SYmP<JpC+o;LpHPp4#WO6e5w3eZGB}4HdY8*L|8b*yH$8o;GsKMl5&Tkk)v6Z2?4|OnEr+!KuOdia<PZ^58qDGOwB1br_WdwC8IfA@|p?H<k8n2?RBd;QFpeB+xkdvI&GKrc>P9pE39w6@`XH!kG(o^JY@(&EfKT-?G*Qoi_0&)TK@)?RVsRzhP)5#_0km4<l*yxBf>Q3@O>K^J&@=oUMp>8G*cZ9DahB#unBVrs8<cJxLm`n~Le@&f1RyvJ5nmU#`jjVJ6S?M_PSaJY$0{IK-=Z+Xe9l}sNh8jQ);BUt;6i;O+4q+%ZsME;vsozkik*9HN-!K%<WhnlZp?DTGh#bT@oW)SQkh*}pjQSmQ0eJ!QzGEn!$51?lI-NY7?M-1Q9!dS0Jd*71v`+riv1EVpP-*~qDA~_xZTzU8ll{p38H)QltzTd25OQB~PpU7uC%GH7H(96lq4p;CW?mnLVk<-ODC%(XaJDy!I)<!tYDs<{7uV{g{<r_4_wRp(+AP2JANKzHFJJ#`;rz?Sju)VReZ=tXQ%3Eb9h-7jEZRo(R;>LOew>4u'

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
