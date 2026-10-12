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

PART_NAME = 'part_001'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/f98f9602167641529eb3f8044b61692f/part_001.stl', 'relative_path': 'f98f9602167641529eb3f8044b61692f/part_001.stl', 'source_sha256': 'e9feccc6d0f97e1cfd6ae40604ad1e7177e04aae3e10ef62302e7fafc3e89f7c', 'input_faces': 464, 'input_vertices': 351, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[0.09663727879524231, -0.3816683888435364, -0.18985438346862793], [0.5000000596046448, 0.15871968865394592, 0.15970055758953094]]}
GEOMETRY_BASE85 = 'c$}r12Xq%j*TyFhTEx&o7ue7edI?QHSwN5$2vzBu(7^y9^tzxTHS`uKE4>P#6T~b{I!f=b3L@~*1QewC?%ew<-|nL4eCPXe&Yb()-`u@BJ8kE`VpPM_fgytbLPgCxy~}hD6+)JbB18=A(yxDyPF><l_wG9+Kx8H^{~SA`am&c4)&XLm7#7yKOMIt(VO5o|>RqdZl~lsI_UYHZUv%$|efo9oB6;2D&*Hn-JidE$-!8Tv9#OGeNhP9KNo9ocfBXxwo1j<OwY`RI)ta&AQ)HX6%-B-H&5I_Sl3dFYx6jSZueKd0p8R-GiaWm2G~%Lt%5pciDvu*>UhFm96JIYU$4{=g&J!P(hI#1Z0d6j?Mjn&CTE|H8@a7eW>s?0;b+^-M@WD~ZjjJ^_d+s~zJ>uH^!qeRGde+xRDDL=I-uRgh4ohG8tJ_vjJ0lMf*Ipi;=josIafc+gjs$FX$D4s46Bjr08t!<l&dCE5ufFoctL2svH#6l}>}hB1&>!fzjy2uki9hmqKjk03*As7C>9ddGa=!57*ALZV9+SrtFBTr#L-#HDYMZB@J1!wE1{d<S|8foHM<>R6;#)S{O?jS0d-}~BT7<Z@?3$<F^d=8eXnY4$@$|phegknUv6g4N%thud8ke$jJoCYfP9UzgPCd*sAENVrNBqZ<p7|ywzt~Cs>?i#_{M+2bMfug9`K%<RBW`?A(=(ry;GN0LkJ7rZw&ghXPwVRq_pL97o0<2~{8z>%c=MzzAg=D6wA{@tb0+f@X{WoncA^k*<5BQBHy1Cm@cL@{EZ)PrwV`#SJsX?k=E`N2*H@*G;qG>d9`$J*={>?Wd)gUTjJOp#VVXPMzrNnY=X*)(NL|}_tEWBZ&hYvwTQ<?1$Eq@t){!~#);3Q+Om5EWOK)s=?tA<yucOD;w|nlJoJ3q-Rd2B;{%9#$U#4DVhbO*;ATDzJ>4`VG4yScw9RAspUvJig*VoHNo_G;<k=NI?>z?*2x7HKav$pcI-@m@z<hl9@ucI~fJpE>-E>B#$@R6tA%ngAi^>cUuPydU=gS5VkK1)60WhPyqb);S&;h7I+{0d%QVRJq6!HTcU>#O4PwVr-k6hd6=>*#I2S)SIBI(Lv~KI?lGUUyNKr+NBEIZf+JY1)m}h1NRl8RDJ8c^`VzZ$0JBT8_BUZvAHB%WAH3b8BSmPI`{h&69|$m5FOB7Ve<-7A&%oY}fah-`lvA{Fn}#==xG^i0gfVD8G5(tBr0hhDJ~xku;a;jh$V%orf;d`d4!8U*_ieykfg3&!-F4kbQRzadY!{YM)uN*IEys@;Ak6bIVhE%pTh~&$DkRUhiLVqlfDy=y}D(wDcUNb&&JS9LVii(4V+I|04I#+_d~$3BtpT*C)1eKj+^@ey7`<zixlJpL*-kQa2Y9AEuE1a0QKvS>WBXbiXgRQ@r@|)D|~4r~FKL)nhlvYN54>i-GItdaE4Y=MA6T=sUW9u{eqs#;3&9Ad~xT;U8PvTrWA2-w(!0ejkj8<~+?he@p(%jO*N7JvD^duWStBbCJ1_xR!nCW*+}B{C>UmEyoW!%k!_q<YjKIXWnm8edp8EF7<R0aieZ+@{K<_Zgq2!b1Jtldn1}h)^Gcmzo<p+5kD2zX<fvf<NiEcmB%-6&}hlcGrw{Cge&ws=B@X6o`CBadQrcLdyBaJdxOrAJ;LijPaU|;&8>S``2Cz_8?{F}5=>lAJ7G8Fd9Cm{twAN?>fw{rPW{gd^QfJDs}MIcr=xi+wr1h+ba?DyiZ@ry=6<OC5$Aa{i^uiqz~Pi<N<D6mI7rW{zluwg+!)u2<GVlP{yleq+YfH_%gz3`=XqV0*7?3wPg48!%IW6FJj#J_#Km7?6R*<*ey@X@9ggyR9k!PHq0S`YTJ?N1f7EQ<H@mqq<O|+sg1Yd1PtD;xdOaSOzmr$ExgLIr=81J<6pvS*c^rRt<M&h_@p>8c!<a;V-cD_K9;T~8`IYvo`FRJvvzO<|nYuI|ZZbD!%u1&C>L2lbJAE^^e@{Uk-@V)CQvBuXoPTD6-MkK_E~WTl&$&I1ZqR*2;GAAG?kh8$r|Yw}rt#HIW#f6|@QD7@eo<{Mk7s0d;%ae=##;<-#n1IJCvkIAnGIAQbCS<X4zIR@*TaD&Y*X@{=j)sE^R9~H^Us4G9N(@luiKa>GwHdi3}BvIl=q(^Dz(Sq+WscI@4SrS@!d3v+gah{9*Xa;E>3ZAt<`_{zR3sTDbHw~+Y@5Y_^KjgjhmZ;D)aarpTqM+%;r2FuOMITKa|&Ft{*thu|~8`^t*RAy17>KJzl>zZc}@eW`~GdWeV}Qv}(76p7*okoTv6^zP@vNdVh*oFIT{gU03*dW2Vsj6H#^A(*4rjMnBg|Ae*x!og*A>)lBAoJb#ydf9Ov9FmJr>i`Nlvo@Q>0`HRPUXfrx5Sl}kO2CklX$n88ALFZ<1GhsaCNgZ;5^446>`+2W$I**A!<|eoTZe}Y@T#Q{9M|R}IJsy7XEd4$)eweq@&CS7q{9Y*<dC<+(rG1mRA13al`-ULTIL>d5;QVj+CC+c{=ll-0kl!rA`5mqyzmELok2N@cP-Q-U)IY-SZEz*=5B?p~Xe5u%t2*5Nv^{8jiFdQEcXPGjuXL_3f*$ZZdftfJIWG_U6-G^=`|fMO_uaRJ=D(i%#6lXE)zQrRRHgM}3`^#7BDm<wTme_d_2l+UAI|G^Sr<NUr0vb)_*r@$-^2x9QryWk+|Jm;yngp>Hz@zC^&CIp!794{#PoC?Ho=vNUasFcMBI2<miO813A|r{i-RMmpT&it{M<*6@O^h5;&oB5*GL+V!q=GJi{f@RTRn{O?|#JhEj8#HvK41+b8|g%7p-5j-8ed@8{j75jS3uZ{7bwV`i%2`kxc!i#5UyTh)Z{ouD{Ih59R43`u$=S$xd8!tWEuFjG9R6U03rkAHeHWch)JmiFGP2@H#b|c;7zYaQ{AF-7UoN`d)euYHd1vPxJX6a|PUL&0JqvoVdF3291Z7vp28b>D4&CL`xoze#bs1o~t&;Up&S0F#YfR{<`-u-}jWzslH3fZa3F6e>j`&`>fn9H`i9(<8>FWAMnJ-f5pEGCVoo4=PW1x8E^hKJPYU7kl*s<*OA}h2J#E!7k3)-b48Tq^I@-8UN7J}xB{-XY|43dwdeOynZKuyU#J=9DR778iBYZ=?_<BT<M=JV^S<%87mv$z<|eoXu1ELdJbxFW{lfUYG3~=9xCX9)TZ@Nqp6VNDpHYgp;rX0)0_UkZlFmKK{wVq#YJywf#y)Us9{1-!{Ek{ykiP?gE8rTq`XrIt^Ew^Pe?8Tjuj#&X4d#s|@V*_oYy!0-Wi#LRTm+x<#?GStu{!SNc82fd^Gskh;)=%H1h-N%*W&kZ{tuUP|IeM@mileXVa{`+?tF@GIyTwO&2+(hZts<f_j4!yB*z<wH+}JDPmb3UZ*hE77VhWuLur3ghri@`Qu-HuZ$2MD{iA~$;KpCf)u(AMQTvvpp>vKocgGBBSE($-%`rLooOZKZ9K{D`Bd$h9(EGxgR+Q(7j~n1x_1v7N&}jO7X#M%iW;a*s*5&hITp8Yfz%9gUh<CW=ix=IB5?4xwbN~0<JA>lOl_qZVdBEqYorC#1-zQ}`zR3tWpK0UUazBF`;MO?i#;?_g>(BW2fVlaDze9#}<@h*-`rmr`Xba7g-{Ls_&S~DSmaDU=oi*aQAM#b;--G?S&!V{d1Bi<Q^ZEDn?AA0cCb$A_%wn!)AI$ORBl%pKd38s+Zun^KpRgUgjza5fqV|J}aON7ga_CFuA9m#5(HRcUq;{R3%+D2El)ghLRlcWv*x`EXto%OOmyf?!fvcG~-l)v+x-VWwy!vnr-*?(;9+$x1x&Oak%k3}o9`A>0n=*9WiFG_5rhQH0qMSU%?=^63I&<p;c>2rCXCCF>rwc=-5+8ew^JKWh<2B<fjhFe&4Q@}f;WRGdr-rd~-|mmO|8K3~_w2P3G@ngy6<oW@+$!;u^Q^ef=kt9HyOaGQ=rZ-!-YEWVb3YI7=inB&b&t7`Jri+t51;SFfphd7Oj(kLxW2R__uKd^+;6qRh--T?)9((Y_crPW@ey+aT#IF{bgKnknD_Zx#rRwlRgc@#>NbC8xbyQQ%G0zB-}lgQ-mmVLOQ1Yj3_sV4jMNWSr$^L&4cr1Z!1Zr>aGv*z^Y5%wuW6nrt^0EO|CqCy;#+5=`Kf}N;0m~*_2)b<F426`9^~8Z=Aub&>VGx%7{8anm6sfE-RF3Rn~SE=_ZlVW(Iz){@(5oZ?em{#|51v?(s~rp;0EWhGH@P;>xkFFIbKyp@qNb};d5G|Mg6Z`8_#(nmh$(JJwg1w05`xjaFKg5KUbP5yq_1m#_!n<NzA97=lABotNgwOSHTr<^~w+2&I?2M+!ef=@9X2%yUfMe)7(GpKH%@6vs3sxu8(Wr`i2|)ym@m`e;Q$(_`jd{xCU;1UH%I3UslueDpiuWKX11o?%$Uj?%$VGaR0uf`r_a0OSN?7>URFV@NsQgFPe`V;9~1);#$Y-+z$(L(|)2}*w1`n0`D75f@xedAJ-Z)R}TNk&+B_XI^6$$RKfl4M~D00kLHK@uTmc0ImF@qbBL&cc;7k1;r?@odCDOE)_EKJt@AecTjy;j-hbY9^83%*4)>q8efi&<x554AZFB!|&g1(X<Z%D*Aj^sO{SI=t|96n6^Cxlt??H#Z_4^Lo|9epVmw5A0@-=FQ|2u}m{ogUb-};UL{?>Pl$H?RVj^S|scMR~izGHy<zhlVIf9g+%`}<RI;(gzj6kj}jUyAblD~;}#`wdfb*pFzJ3?f8yjduML4GHC+WB>V|X!NM?zxpQ{6)IKu|Naw=ssTb&wo3*SsUHirWuaw}`XFp(Xj!CQ2YX+zmUh2gCb|4cC<EjWLyv~PAKHnZgqQ`eBca#9ABXE=p<@v<8F7x5wl%DbiGq#-?~J(CD3UjWmNptOt)Yj(?+cv-KM8r9y3UCI0&#s&B<pFHA@F-5rZ3o6@TH!DYo$LO{uhXu4&5KVj2{Fo*+l3;(9>PMtdFtF2>6bk2!9~_80e|+ry|DDtKe^dmTUriM^8nLvGC)eSGxQOh*^nir9Tb66T1s_TcB4WW(%~mPf>RbTC&yf9lZtDeGXsh1nAG9x53|rYaM+6{#t0sX2T{xuZ2IuE*s&GhwtdMuGo#pCGAz{tMD(ONWB?$2J~j=MX+B&FM^&0I|_Oh^nBRi(DR|!3tofLj)ol$Jsj8cbNRhdhJ*Kp?GCHkB@TKNe5WoBTG~%x$JnJ4v<}~?le|9srgmupT_3tT{7(_v6h&$cTH5AziG<%A*Ea==1Z!oNMyQK~mbN8IBw{{+9|PUU71Ij5F}SR63*XV7Af^SlWF6r<x-DYb!|w{+!sT~FOi$Exh5s3JPgv>8bw30;2L5MYJ)xT+zswa4-_h+6Cs_l;wSaC6+t4oc1n;8_!5V-y25*2I^)P<*5!(c;9#|t>Qx7^8aZ%9S;5USp*AIY>h3*YsmhOn@2HqWGCC9xDbQ|=IWbNR$f$jj^0Ws3{uuB)z_W<hv76UujF1=7c7_19e3~W5KtRD;33pyUxevW!srlIb0XvzA(?}7I8ftEG_bsGG3&_m%5MU10o!yf}JStnQxdJO#LU^1sJc#j){G9K4U{w4fT(2|YDSPTH0ftbGq?}KvxdoMu#r*dY0fjc^jU6(e1?O%w!in_ZfQp=dTuuoxw?IK*)2fOM7w6wcmpW9|DbTE9UZY%262!0oCfWHd%IqG)7-vIwVg5T@Y;ZMOeYh3I(;-q~ifVH%*z-5v86!a<Nk@mXav&k!Hcik}9B<Kt{>s?2@^smF0d^_}ZTqD^*moM#PSjiVaF96Sh^W`hFKL@nz%bWqsp2L3!EC+Nj#z?XQ7+3i&cHWncFRdImxn|^<A_n~_`*I@MwGM3xw{zvOOQitT(!Ot(BJicI0$=KKcF7Kw9bD=l__F?)U_UQP5cq4sb&_4Q?JdFV7P!<G;LG|S;BP{?0KO1)l6?;?*-ZFSe{Gi(uoQ5qPs5k>7W{8fPJ{15on%j-CA$Y->P+@CqzPaq?Gw~z1<!<jm3|qNtl*VUCz<_|M|@(J4zTT^J3zOA{S>+lbTind(9NJfv`b;w4`7=@7ebxXzuRqnB$!EC81>(Q%le&yeW_PKOSTNY)bs3;2$l#g^>X;KekpvZ7u)4WyUc~%3q2Ql3Cd4)Ne27L#eM@%hJFYe7{K}=bV0jRhYf`dgszA>scYFK3M>j->Q?Y&eLMIKP+EaEMxA6Wp(U#iU+N=vdk)!UH;QSOqhKc3QRu^V`4zs@sRG!)f$}SOKmgZCme02N1DNFpmpTHztXJWeM~MKhfjY_RLQD1$e5o7Sr4d*oaH;FSm-V&bOKsR~nq!w^C{pi%{RVmu^l{i7(8r-~!ajh$37tBCi`0s33&5AU8hojn*rftk1#qcr!k6{+;I}}j3EmcUl0`yG)*QanA45wf=d*#iY~Y!tu8+8uu+5>v>{2p-_suX^xo?KRmpTZ()N)@;50)NW>Oa9{{V#(3TPRXXegSoo$vyHs*m-cNPr{e=XW@U3auPfRb&_3ymh3cq`W|POJ79OfrG5!t*1sFT{u7j!;Bvo|b&}<VmQ3!KxuNBLSsbi5xYVWL=Rv<pKOChrcoEb|R?03V>{1N2D0DICT(H@ob3tc>O$VJ3`h{TohhQy>)VE=OhQ1Ab8TK6XW#}^~QlGF(MY~kCOBNKVv%$U(oeerWY&GcY&^cj0gw6?_2Udm71N|OsE$H{4^TU1wogZ3(tqZL{7li#7x*&8R*gDYChC<6{%!KEz2ps|YE_4KRIoKfRa?qt=(?gerE(x0!x+HXQ*g)vw(BZJDpu?ey!ls5U3LOTU209G77;HM|V$daEGeDPsE`>g+jeZG*E&y8-x&U-O*c#CJp!33h0G$^)H*8ht+|W5-t3c;~4uP!%9Ri&dwgPlk=*+O?p)*4V!<K~(hRz6E3c3{fLF(#uDPxyhu<t<IOO5`Dz!rv%Y8a3zB=x`jFM|K`r&9v=|1jvk()-!kedTgH*PD;nQ4Q0`xnoa=RP=!+RQ8nkFYB~Us{'

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
