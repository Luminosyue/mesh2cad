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

PART_NAME = 'part_013'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/8b8e14ddf5104c579a6dd100ff8c0bdb/part_013.stl', 'relative_path': '8b8e14ddf5104c579a6dd100ff8c0bdb/part_013.stl', 'source_sha256': '9d13399f53c9699d4a46fd228201d4bd1ea4d24fa53f61ea6abbededfd8bf161', 'input_faces': 358, 'input_vertices': 242, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.07676451653242111, 0.24577483534812927, -0.09271033853292465], [0.043340206146240234, 0.45844796299934387, 0.06968113034963608]]}
GEOMETRY_BASE85 = 'c$}r02UJvN7RNuZD|R9p6M2am3r0avv7loE6$=X1WM$A`#4adFK*_VkhFAbA$U}<Q02M`Wl`*I&#;%ABN29D_0gM{m&6?%A_ivb)&7QMomvip<|K>k;?)%>NzBY64^r%$XR`A~^qRX#)tR3xykYOWiMUY>>T>nXaf$e9`{?1C&BVYc#*N9=GhI)>(5<w!Q)mMIjlLA_GS6cO)?9!^8(rWUofVly_Gks<SeB~#7H{a=je&v4P6yMo?<*!?Jbne(r>C~p3vOxJC|7w;u!I+<PAY1B_=C^y7tJ-?mHmREPzWvhICcL^OU+W5I#7Gru!q~6(5AsD);7Y0b`_}AF%4Xl@!&T&a6zr3};<A|iO};bbYu&M(<m(S?r|asno5a%fPrH(@<>qnzz?j+cwffS5eB+SN+gvA&>T8Xfaeh%C`HI`{WU3QYoJRRAT)B>yPb9t0xJ|w?1NZCjB$3*w-$cGvki+@u{Z~sh)E>!xlU&L-PP3wXwO>!JQ$K?9N1vklhM-oc@5=3b`gRWaAuY+*?_I|EE~|W~Zi9kU$`5~Yll!g3cJl4=$=4rxLivVcwYE|_8&~E0VsEZv*hTsJl9Uws+=d2pT|?hp3H1KUJ>(nX(GOL=T~DvaFXsGlzp~#ZIf`DdsLsC6QEHFw^RqiC|Lx7ablt*Q+@3WzchP;d%_U#2??L(cQ}yUR#mEfujcezTudRH;&m*K4=eJ1Y>&|tGr}5DE_dQfUp@i}c?mgqEPGA7}#-OwtRHx}z>2%!-L&(<_59T^2BX?8Xx}CUAT5191FX(rO>exDQewQtLU!KpB>AE_5_J2#dPUC0Vq6`{uV?W?J9b&lsS?M&+48hene?S9%Uhe!njL~oD`dZoQe9Hf2FxAmLn9F`i-X+TKScmhQ_^@9TevSIA*Q<k6zqA_p#(mmVs<YOa?pJg#rvBDqtf`JVPNCPvenq58pO+V@-`?$Ee`-GaDTlAnxOMZO`Dw^a!{<(2CjZGr9^dw>xqiE!xc>1T)J~Bxoa@*>qWZdLO}X8{g8f0G__`5)Po(~@bcV-^=0Uz%dX;>me=PahQ#Y>j_lst}G36fDY45+=%>VQvx94ovRI@t2=W_dtE~lCL`W9En*BpnM`Nnpc)DKF1-~Fb(()tMb`rgCL{gOE9f92a=>1K7NB#^J)-Nww<^y|!?;~(wu-ax)~G1JU9rialu(dUoOFv~Aq%j3r`#w=e64WRL<e|^*Zx;vuSzjMT_j#A`D<6mjt@_<?Ws4Vu2)I(-<LI>P19p``4(K5+5dLA;nuJX(8<f~&hrkK^K5=rwy%^96+cE8p3l5ad`Yu?Y(pYlBVTZCqo|Fj#=>&?+?&Fa6ILcZEO-)x*HLgoB=T|1iHZ(b_zU)Srb?QL3T)>Y0wKR4bi|HxzZ+a_sd`G+g>e&P5y(bU&3ZNlsAq`|w){BZ+#{on4k!L0r3CUTwV%ezhUmC|_5*Chv-<)5~?L-k9olT7oC<88?oStoultJ7r+=PzB!`^Ck1e>xv^-nyNCHh&FvWyyaw-;D?Mk#D&^DAw!wIe&hE=i~FQdHuHuXWwF-F;1Gw^)1#VZORm`-!_ZqslO|ala=E+-(r0;MDqBuTn|N|3t!h_{WRR~LcYHJcAnQMt;tuGyxKwf3C~|8<TlMaaqu4bmg}=te3pHS_1sW*)DF}6YYe>0bvn9pzQw*Eyt}b)v5)A29JoCe`;Jgsaeaqip6~N*xIN*Ya2<>N%aB!<eT)50&92S$E%(RDFOn$VVn5YtKWD$`RLa*c^{4g3p#O<{%Y9k(%VYn}NM1L(6!ZD)P#^ODZGZQ&Cg1WrAm$!TpwC&HPt=<c<XfI+^bgi>zQy@Rmob&<{o6U}`YS#+S)9l8_sYn(JiqA<MDw}K;vA^dsmH#>xl!k{ERO4#pEK3C%5gld%+ITa;v!!EEY7zEmt2ke=LWB11KaN7`^zEU@|-Lx*Ct<ic#QLNTBlKd!p&H!V{zWrMCdl2XS`18_q(Lf{q3}hA>Uy;*PmES>y<XmBbu&jasD?}>a~^fN3Q4VHtVpH-v6TEX39UgfPBSuKJ|mvr)VSPTYT?O!`{$(sXslD>&%!&zVMn&&tJd4E3f~3o%y;Uh6t+TQ^xZsZ^$?Fyh_@Tuf@;d`-;t{e$!bUq4A>3o=(28^da?+_^dyVBiFCFohL4)Qol_&xsH4rU%u|>@V!(gcqIEDkLNo21GN6@8Z{(eiE^cN&yd6ONVn=|+Q;<WCe!*Rp1q)Ruqx7de>)z<`(}~TCh|*8uckWZ+<4r2HP}J#cdi{q`Kv={9W!=J=k?axcO~8L;MX+oL~IF-dv#0Va>}3Flk2RDrFN>0PRl5NghKP$aQ_tT<Kor5AE=#PZ7E-ybv%yy`$zVzw$XZM^uNaIlHY@+RKJX$i?XIJ^^fSentaXCiO&i4)u|uU$cc+7Khv4p6Vi<OS-iZmi0bzo$Lm|r6t3@|K)!KXDxa6$^7l+(y>TJs7q;Yf9<ir+BvK!#lz;3U_h*ADk)*$!CSP&yz~k1{ho5_4NeH#Gz5|aF%rB8&IFIU#&*pKJ(sMHDKU>lMtoN^m^`u}s`R?84@N;RvbxvpU_%GNrhU&MS#&sH=q30xYUks!CtG9SP?CrFX-q-#zl-e0siQ9ST4LvU*u3kPS-=49R#+4|UOY69JlhmL3{az{G?_xtdy<ggUBt55=+iAS1#S3V^7aygKrTiDEynj{NK<lPRZ!?kn&S&{~o&S#JvuNZ`zH$9)ZfBX@9{SvC$LZvkMDukE;#F>c>KyWGo?<^(*-ZZ3ckJW*tn+C}-=l=%-T-=j?)Nx9C6vFnPWz2~qkUy+kIr!kxATl`5Vh0o1)T@PuPtc36QR!JYok75zsCn#$bZ=98_Kt;P2*hHTX8=u@C>Er)L<WtXVLl=&&M&N=suK$Yka@ozoqu5zs@ILb2`M&(QU>S^4~RHM0KjVv0rZ;jT_ZUC0|?FjmER?<XOJo+>Pu{T#os^Xc=kgsKs>M<8d_34GWvmd{oOO(fh_#yE(sbGVNbtzc;UcOM-FTN2|F1bNKg|L%c7Gg?DH@5}jX%k>9z9#*eQ5HSV{RNZPNo!EL$DZ0Ano$6g92e{6LgZ<)(!KPcaC*HAkzf6V=SX+8b!A>s$q`C6ai&vmXQQJ%W>AfLPEU7&Gj2;lu)4QjWJ{Ja<ZT>6io`l^yazE<@!9-k4#v`>iQ==J2Ez<DXyaT?V>_&9><Ox?=&d(4K`DfJ)DH1G9Ub*a8?cmeIxqJAX%U*^y_R9!sj+$+YrMNyp-Z@7-GO)zQSWgF=8bJ8!+>&-LPQ2j5{X})UH4K#iX5BPi|yzMtp|AgCczqRNSW$J5F+<81K*_>#W-*^RIH+VYjU*hlt&JU}>=i7!g)|>kJI<Kj|TJuxdFU0js&i5&%`&H|N&~s6DZKe6AeUnJzN_G2?+Nr)vqw%YpxySp_OMja0YSvHeuMXt)xD1;>^$k|h)b4RBxgXr(sh@?d9sMq7tcv;guz=P#b^Ju~wc>~TeC^(?qI~zM?9cq2pYM`7+@Eh(kgvCE#_hj8kJq2gjcNba&%Q>_ODvvA=N0wCA><oBD&>C2<b7HcSEBE2hOl|u&gFF$NME<>WAc?Hx41n4OKD#*IE)})AAXnnVUY)q=YVMT9e(Ef8l6r1jlnyaeY-RC+;w-`(>zk|Ug!Gplj!-XS!?LLC8k!R{Zm_8#`pU?dkM8CYZ&_-+VlNh!91EXoqT2HPF@F|wWj)pLG#&9=lLrRgwnpQW;Ub!$N1eP9?yA|X}%ajV#(L;UFZ91W))7?eSDLAC8jg?Lv&T@f5Z1PXx~sy&f@kre?;TTP?$o#F(HT7$+NZSJg3|3K<lE?BZ0?N|6Sy(4gJ|)mB;OQwHND;1OLwY{9CFo-VLJjna=$eK1cs@l<U7vCtsvF()V4>HJ<8=4gDgsJ<Wb?_w5=}IIw>C$+tXe2wO4P*W{;mY0AI%`sY8j`#b+vKec!2?DGHq)ZVGQ4P#|DK)(QY26u(}fV+abLG|En;2zLP;2z+f(67Ng!M&i<!M(sb=uEH<+!yKx?hEb*^#}I@4}i`B4*<JC1Hf+JfzWwiso#PJf(IcadqC%cr3QjMz(Wv{heE#t4+Rg027`x#M?k*;j{tiiB!3TG3ig7IL`V*SE(J?n1eUr0EHwx`66y&J0(*joLFa&nfd@lpg9n4%q0_+b;Qr9b;Qrt~&>7%9;NH-w;ND<Y=oGLkxI6SKaCfi^)EDdm?gE_v?gDm(jt5H}2X+Q`L`ZgmjsZJDM?=SerA`Eo27d|t3s~wXuvBmGm*DrG^~QCib^uFl4|W8%Lr887{TwW{6<BHuaBFZor~}v$>I8KFOKl5w0>AH{w&*jdZNO4LGwILI(DzbXnmmh^cve!In>@Sbc(zg%lV>g271~Txj19@Xp&yBgu_U<<^b=7r_9XX*ek>}+s$_TQhoWL^OCAjUKvc{H$-|&^M8({ZEa%opXf<dZu+*wxsn%er0_=s)SAkXoS3{0uxdzJht|>yYEp#B*7F-u0xfXN~SgHrO7Pvk_azp44u+*X8hTxje;ozF!>d+D3>R=nF7uXB;WCImo8*p{hlxhVPV1d4~LP)NJkX#vB6)d$jxH7l~v;nvVxE|CFTo2p`+5{}MF<9!S;6`A3Xg_d2JU@GAQ*a|_J!n&t>o!HZq}qa|)-`E!U6cE&i$0KA3oNz1N&nPGpVh~+w1U<IpD2%O<&g)y4bB6fgWd<917C#}fv<uuKz{~b0H1;00!zIDJ_9}pJq<nyK8BEd7-|4Z%>o|=??p&Xgr<O{CW8~f+Yypupz+`sa3n(VCWPcI2+2tZ$!XAJa5Ao)hLD^A%>rkDk0K=JLJeR8?mrhH`65E{4d@l{74-EDgye_NpTQ5oPoPEMC*Wt$``~Bbr_kHrr{G7>Yv4y<BSP{W=w-0f^WZz+o8?gey#zfEJ_S7vJr6#QTE`KRv!U0(Qcr-h!8;L>Q=xfaspr6{;DZRsN1#{1QZImyfHR?Iz?tB5gyenDlVGXG!27_vp@+e{!3hY-anQYBsfpk?@HXgn@HX%UgyeP57_ihx@H+5ngyb;jCU6*d6?6-DB{UYg1uQiQ91Gq9O#|-%A3{j}D>MTv^(gqS;2dZ!I0t+dAvqs<5iIovI3Ii$A-Nd(5G?fxxENf5kX#0R2A291Tm~*hNPZ4|1eR(9KL<aC-T^-b{|zDe0rV#L{k(dBkbJK^3Zd7b1z@R{z}LY)Ate7OD(2*m2+0Q!lJ_Gd?}8o&OU(xF0`GwC1n&TcBP6eZrh?ai*CQlvgdPM-Jp$ecjz&n{3e5y>1xG>C!BY2uqrjUHk|UtI!BP{z5#Y7ZIPhBVa)jh%&~0F;8^FuJKOiJ8fvy8fT@79WUJMNbF9t7!t^zLvtD<7wstC!U<uM<+0=g0`H5R-Atd)nShn2N$rT_FVj}?C^9sErH0n+l5=0D$<esX4ctv`Ou@${%7&x7R$L~Hu8TPD99iGKlYwY#?'

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
