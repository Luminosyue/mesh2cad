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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_010.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_010.stl', 'source_sha256': '26f9575f49e42f0a73164c88391d9c467fdcc227e2004cfa474fa99c73e02fe3', 'input_faces': 468, 'input_vertices': 303, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.15352454781532288, 0.22550800442695618, -0.08965746313333511], [0.05342072993516922, 0.460971862077713, 0.0643310472369194]]}
GEOMETRY_BASE85 = 'c$}r12UHc;+J*-O6~s=A6^|9WD7LGHjEY2qEs3I74`MHXV6S8E4Hdf{L{Y?Ef*Q-%dqIfCSnjcV)kLG-BpNmM?Du=Ui6j47|N4K{`qumK`ti-4J$v@-*|TgNlGWWulb@2>%P7Cc4~uD<3UAFv8`2|YP@jk%u~j3Zhr4Nc;j5qbI=^Mx7OlhFv?1C^zwSL^BVzpO+58&xtm{|V=GQYSW>8FcWY?&e?md(r9Ns^+hs%%c9Uk4o^?UgM|A5N2fC`muqiz4kA1_xE^leE;4!YFlfBeelE;a0RmZ;wiV={clj1`xauk{TO|8PI?qt}an;plwzyWTEB{4P6CM@y@;K>e=8g}`_AKLOvoSkr<0GC|@y7f79-Zm+`Mmun2)UT5|9XwStmaX4<ny5gtD!`HUoT!i}LeC4>~mS!OTKtepuCwnoezjsMG{2>p~PGdnq$uFLaeC^IBbMbp{7RgVZjC^gA?=rOWv?hMf8Iu3)p_TA2ygQ8J)S4#kymMdL-|3b3EjCJ>K~Xc%?q8n4x9^F+g#6&PIIc14p7>*ve}Eq}dmjA6>*AmK4*jN&>AnW-SbI(C|J)b#&BFr|aNK(7lK*Hf`qK;@gnWC@1^A9aL(zWoQZjtUvGeeq?i<k_E#>xP_^nS%olWDUo!z^jKaF4ZNgeHow6p#?^uKMy9?73K8vUS;uDKTZrIMwc&*IZif8o68=(lr=#2>O*e9z$VxQ<umOPxOVQC|<qig9B0n<2*?8X@f*d1*QFw?>JdJQj5f&s-QM&Y)gW=k2VE$ZuJFBK!;8<hbtw<T_q`l8p9T3Kze33F*(0htPh#b7!ezCP^KiQ^Rn)gocv8{IT@IxGYI%XKG#e=JebbkYBF+aJ182p4WY_)HyM6ChGSp3tul$Px7BNh(NzREF;$?Iac~}$&HPu^SHDeH!4E<?eTH+zwxTL9QV(h=inF0=!m+7^GSYff9bbL&oNH49ofW>?r|0V#2UCR#_@ND@OQu5Jr94yF!Y;w=Q(^w+)^1=DJxTOKK-A<Hv^xaMgF7egHhM*fz&BkL)vq)TnD92uRBub@H`yX7&{vGqkZuW`1S)~=pUnVDfs5~L-1`eXQiFF{BhmQUi&4#MvBZct&XBSdbVwnKRr;!!;qY~Pi^rVq&?U6$a!f4(EnzWMdHWYkoMo0G7kM-v#+%C=5ve(eebGG=%2>j<+$@+NPAwmW1MKg5prCw`f`1}r!7YPnZc6Z;S$D)>HAOAv6c87zVpY+xGs83!41gYT~qq=@)Wew7`6rDS#MZf>Zj%UQTp@62>f0kue38P7~{m2{rFb=eMv7lZeTOXU)X6H>V&*9@pr>+p?~zOD`ecZ_#M7}_KEa^$Ld+A>wX)){mmk&^IiXiINz@OrOxYL<$P1NuST6G6U6_@UHm2`WS-PUNu9D!rH;=Yj6)-!7kr1?Yw6EJ=P=G~`y$|*7eb{UoTo9)^=~@BcfMRIbvBmlq||=3ozw}MjPdDcm3JH3dCMlpt$$zg7mSX^ad+Q1h&rvCT!X*8*%bKyI(1O`@169+o^+hAy?4Ci-&%z6=16aZ`pyQr_+M<sII*Y2qW^6(Z15f42XNhOdy8#Hds1^teworZuD<H+I^@6n_W|g2Z)s2Z^eIrUpWxe%oq=!UDkbBpf>Zpd_b`vy9z~<RJvB-E?-pWQnZdO;<Gf-!z;_ntBK7~+J_`3^YM>l9d5PRFDd#Z`je#%r!=IXn>u5G9f^p*9b!ETYANO#*98C+LA8em&gKtkeF7+$dYJ>jhG9SLVI2!YtIpSAbcRj7U)K6%Sd~<&AV&vCqAo)jLVBRpiS7Q7a6N*W`S@b&cR~3@+6SsLE+H=Gg*WF%Y#tzhfIu*X-aXaK|{_Dpgzk8VEyDyghymx;A`r$|o`1<WToX5^#ougOF4&T11gyef{$M`fS-u(`Kob;#Z*qMkr$phd!cVv@xHrO>6e|P)my{I>3sLb=rrY53}`z`pk?>9?3PaU0uys8)B+XqyV@isa`&TG+H$=}ur<IQ$!4f@}4EKdBQoiHBk%YK*fc5^CxXT%H{Z$_!r(1n3g|I^Ait`XQ$o_8s=B!BiIY0s`XlW-n;s)_H}4R!2mdZpms&y<(rdNsm$b5?4F@oyB(A^BUI%DCFy8~vtN%mUxh{wv%Uj=}48;`hk=d!WIg7;pN8!niLC-&OE!WpbfCx^H6#bmVaHKi?_i&BJp8j#I2IeCLpO8J|Z}(QoG6`@3<zQSC5KI!1hk<C=puihuu*obMG4^NjiJJorw{<A#i%sgcmD6X4s<`Xk@ro@Kp^mr?M|x|L<V+K?jamRemT|5>86zn#Z&<R|&VcNB<2`<;Id-HN~a=20rzbNQz9^YlVn@ORTP;M?Av#ysZO@EHB<NIfL^16jXiHjG34StI!7x@vMCjX$vz{U875x5zI&82QfJ-W!qs^ELR+fHF8=^UDQ`aGY$H#BW_g`XSmGj^l2dDSoSJsAKQ^8tv4a!{OU}n&W=7jl8}K*YU+b_>N0&rJYwBtVR7LRV9B*hFr%2kywvu36<cRL+{~!(SyH~=WMqdsORh$B-g8ZEA*S*=STRq<P6*w&fn_cx;tl`f$vDait*`~RTcMzadL;`ce{x3=_nG4{&b$+F8OVq$h^0ymaHrCEP`(z|E=8DJ`FeF_-?hNJ!i&9dtO~xfjoO|sqfWC`tyG9eDsImCi%hJ<v#W5C*%L|_fXr?rpUKd+_?tVtzn4x!%9j2cR7gliCKI)&d(7l^M<W<*3CGNu2Jyqbvnwtar%Yy@2=+XZ9j~___yykhIZ&3J;g8hv)qqw@*v+B{RjF<pP5VMtHCGne0Q9=CeN9!BhViGWCrFF?QWX*8DroZ8}rP>zaJh7-&wJajNABbGLQW+SDv52&E&fGnkUbxtF^`N7KQ8RcoHS;cvS(uy&~87%SIw!Ym!s){SCRk7aQYuqqCdjm*^?$$v1)P(f%tJ<oP_@UB=;peK;@Y&9ibpt#2UL<>GefU!PPN7oAh&`c8<!y2z-uQR?(BFVCH>sd8UUDk*;Mx2WTEyp?%ox3|<URY}If(0=Pa|GOU@Cf9dI<QTN~;HxdDGuIIROn1zCj+-rT-i|DRGCm*Vk$H0OOROvHJLEmo-s7H(WBWGvX6m2v{Oy>G`^ed6749=fkf-#|y!jvcJ1fXMJoZx3-+kxtva)UrwQu^nZ~G=t=Kl$mwtnFI*OvRSbIi66{D(QvKaRfMJ3csW?;oW9Cp&h2kiT)JtZ%~}$+(T2vo^Ey(tVn*&8#2vXV2GU)^D0mlf=yWS?}zZnA!FEuWz|t+R?YGGrR82sD}xejT2+-rG(7Jm6mT^LZ;)eL_$KQ<F-IxLT2OK2&$Nn*?r-3K5}Gs9~ni{9hu&DH;OqjyH9NkRxi)=zRpz-`z6+Sz=+B(zGdFf*Uy*dl4YK;`*(tGotGRZTVh>ioyQ!$N3kxp&U<>fF!<JaQd`^x>-vx8)!)nFz0*1mYb!>|zJg`mHj6feZ=L6jC7ZB+V|^~TUVyOQ^U-tUx9(W?S)V)aed}||IFmFR`PS#!vug0I&q1wHA^6tkrWTNdeJSg6))+7w{zuQ{m9cn_v_8kR`ZeKOpZnUD6;p9s%R0gEh{ZmWbzPxN%Qgx9V_BaVdmdwd$hw}<?(83h<6725+GpV-QOB~5(h9s8g7#b1UD{i}7}U3{-?WD(2co`pz1L<;B<fq%jasOGFZh;qrq(_^4CiZEmuh*3G)8^PI#$!>ygZ=&weB?vH^IE572Db#e{WeoYu-PF;e0IXZEcWuIIf3feXccs1plM;{O)5B_}%hepk2;A0Dj_!?-AP35Uh(odhfW>EgHV%Jw@yHCI)$y_ZqEShP;oye{ZU>2k%YV6We(BX&=64X?pDmsAG9A)9%JiMEfl7amJ$)c#m-$TO|3{9^t*uXfk{%>Ra9)wdk9ex2*4>TFcV2aXyy!RxPy=+G~CPHR|1fZ+%}j{2#_4KclncXB@`)Yc)a_qP}Gxz?iMY<L|Be39qkVoo?Ni&~hZ9UDkaJt^O<cAMJZ|owgM1vF?*p`3&zX)_oP@O>6kpeHg9ra`@JL8?*5j7{4FwBlUL3^VYKOr0;$p`Ih}FqxQrEoWErs%<zeWZ{0UD8vDxokY#_*oYqHt%YLA~<~aP1_8U8e;5lI3w=`;Xgm2yFG;fcBZ`~KwL-tC(Wq(zFdlkNQKi2%T4(8X7_H|E%!nf`l>)Y(`t^3TT*BYr~*_YOnY9=AyvcGKvbrRpQe{MV(3*WlmuFcAg^^tYoUJJLux9;<sdn3fRd>1f(+YaCQeL)-aQ0iO0M`%r7!?%9F(0aASJZ=4+V*WZ_eCzj@#5M4(-)po!`^2|=-_bi9hHw2IWQ3d)-}?P%Lg8ebm*snt*|a)*>-Q<szrN&KzGvxm9PmH-{&n_@_?GWw`u;SjZ~4Av4*N-b%l9~Ac5^&`tl#hS`jO&WzW12{SH-t{AJl&h!}H{W?}@EH_)7Zy(OmhX3%X`nS9oeZTF>ymeIiw+`gyOJe<JNu^MCb;v}WzP|KCrfdE8t}2Uqwo6c=PDE<*j3th5-p2)P79aan3<veHuIvgC3M#eUS1WTh3ze&i|)#Z{>l$w~{6tCEW{6nj&1l9jrXy~)`aiZ$w=ny}K}$to1TruU5en*5TX_zCqsS?MkE6Y@RkHS#_3O;=o{UZ7qhUm%~MULh+zM?OkDLOn-5LOxCXk$jqbo_d>no_v}5n5^_U`7-$iL-AeeEAn0P1L_;{1M*YqTe4C&H({m!rmyr4`6>AahT;<p#b>EMk<XITsXvp`$(I<4)2RO<D}6{#BVVL`PrgV##!!5n>Le@um3*E2f}!{wHLIKOJF<tHXb!Rm*^}x;_9W+~<{{@M=cD?N^O18g6z8WFB<Cl8!cbh8T7+DL_kUrA;^Ne@<l<x-wH(<-E<^Prmm!yDD6UMcLaxGlzA{5`C5B>OYEg1g-t)c;#d#Tuvs1H?v+<tK&QP3%q4*C?RNeoImA)kZLH>>Ug!~)%7lz_T)O+Md<bP6clHbn@|70l6U?@ICy+BrahWvhBQ2Z@*7xgGv=@IfSaw_#SIhDMZdY-(OypMXBypMc{q4+TM2Kg}gIQ1@B=>zg{@=5AbveF;OC&_!LC&+uqI~a<0Q_qrjlfPpqHmT`krI*Mi`2a)lL24RV=|%EE@_y<u@_zD8>UQ!@@&;Fwb46`elyHSwb5w9eJ*tgt<G<IV)+T>LZ9%O~ZbAN<q4+auIr3-Z%B~pg3d0q{sYA%a$^96LyHI<OyO6)4b|NcnMgEE$L~TM2BG;k*gItGPidutQiky#HnVgSYfT6e$wH&z+*@s$!>_g5^wUKSS2KgC^i!l`YF%$<-KPLx}8!;4zG8DI^)+4{amTeh|2QU=(qP8Hn;C1cAP~6)UgQ%UUUz5M)_3q42+>~0G+?3p$T7%r2+>-haa!YbMY7=rhayYdWS!pM7IJqyi2e~hKFm(udFnJt9@ocI=o=u)e9ZjA{9?MWXl%aSabvRjRKk`6w1VeFqY8SH7ugLAmUosRoqy~|d)*&|}S7#_LN-afJnvYzR?9Nc^K`lU5T8QjH&c#sdP4yuw%}@3w=VT}@NG(QI>PId}F3wO~hN0M>p|~zJfUL9;xh}aeLva{2l-!*fO${YSlOw5Z$w~*1BgxaLy~xwa(-?}UQhSr9lILiD-D7hYiWe{xPhcqSN$pHl+LWxcIaz5-a!+y;wH-N%97_!+$C5`e6i=e|B`Y0Fo<yES9Y>x;o=2Tco=0Bnibd49)Y)XE6Uj=)lIN0Vx?((aBy}u#BsqpUlpI6uLmfy~8bR(u?#fWyhT5LohTM$$C0S`hax-!uLvb}~b+Xc;<Z9$k8HzQkJ6WlR_ScVME-S&=skz8Xy~)|hIT(sPsX56?3z9v_c^HZdQ;U<8mLV4=`!W=lW+<-2P+XJhPgYu&T$5a%p*Wb@m>f**NDU*uzn?oY6c1x4o=lA<D~%*iCeNTwC$FR~r%op;okm_xUcpejj5?L9bPjnL*}+hpNL@fqB(G;EUQL}qUQM1)?MYS|MV?PyNR1^c9YtP9UP7HjUP4~VP`rvdi@b`QK%GZUAg`q^Ca)zYX@A}Siq}x%sEf!-=aQAqB)`A^;~0vkFcgoVjwCCMA&(&Ur}iQDCwF5g?m+EI?m%u$Z9`VtjNF?11w(NIY9Lu@HF5)TMTX+M)KAGuHF92ZR)+e?LUki6%}&lj&c;yeMa@C>BIl-hl5>+kq2?ifLM}orOjhbkE<!HJP+XQ;np~D#m7%yiwGz2JxeB!=xeB=!wLZBPS*He*b#e%`BRPa@XDA*+9Y$6<nLLIZPn|)2KVQUC*OBAN$qdCC7>ZM<E6GZilT*kW8HzViSCEx1BX1&aW+>i5b&!=NlDCkzQrDBWlDD~{b%<LQpRE7Wf9d(_$54arga6=T{mT!xx&Qu`<y;Sw|89D>4)IXq)HQIk;NhI6R(0Bc09Cf=G5'

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
