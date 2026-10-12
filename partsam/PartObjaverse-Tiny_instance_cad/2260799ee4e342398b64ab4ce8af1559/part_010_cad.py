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
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/2260799ee4e342398b64ab4ce8af1559/part_010.stl', 'relative_path': '2260799ee4e342398b64ab4ce8af1559/part_010.stl', 'source_sha256': 'a356d7b64cf9babce677eee5a3137f4a7c138839c37df44e1232b5a7286e9e2a', 'input_faces': 252, 'input_vertices': 172, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.18494813144207, 0.020669609308242798, 0.07328025996685028], [0.14589740335941315, 0.42219078540802, 0.3655920624732971]]}
GEOMETRY_BASE85 = 'c$}q~2UHbj8iogm8WqKY5{;0HF`|eC!5R&dh$y0hy+rh)VnYEzRAOO>AR<P@hN9rbg1y8TyUExRyP`2_EWyOJyNS_giaERUzu)UF*|U4jp51%Sci!iJ??2!Ceda<$n9D2fntZ&q37djUM-@#|;i|c76QdI*j2;%9*d#VS*-5JcUwvNcg6@5~MGSD#CTdfBhDRq3OYmuH^JzDtwU3|8XGC1WgoLQrA#n-Aqm>^LH8wHY@)Jiz#YbD^2L7#@``H2-`q`%0{>M)Rs|og~O<#U)sj=$mi6Eu1Ifs<$Hy3`Pe65ClT$OFT%9~2fUaiFcwsSG+&1rj1sbfuj_(tuF^Qb@I<XLEw=SNXLb=E0dUohn;w0VE=BXpE)jciBYJ37KQ)(t{_`{_ZFC$ELnzm+HXD}QnZ_sw>Z`d#P3w;KWQ&3Ar30{^w|QMPqjgnrqNKZmdN3PXN}_g4A-;vuQu@5yQSKUPD39bNar*Xw+Rei{#Rp(P3D4#R)(0A+obhxo-?;TtZ;4y&?ObK*hdPnr$ioNA(;JtZ6cDp@o}>JM5j<=_{%&Q{_0A+&Q$*q7+fO7jb-a|V1PzCPx~&_*19K5-X+ZYq4euOG(45q|F=^5j=Xze=X9K|XD9Z}`Ubv*>@x*Bg-ENbnVZ?Kb4mo^QlB87b#Y<VoJN7xhnEk@jBt48BorH0qnpnxeioXp8upr(j;~^^IfjUB-()eiiCF@`l1Ude8a{`GcqLN1nasE<oE9ACPsp1M5WdIwa%maz^|>U$jG;5P|vCs!o7!77YFh?YrlK>kR*q@QvbyU!&gpuCk8S4V3y(J5k@5Unu$0T1kFi7pz-t^1*$mU#9tf<e6%_jQZidkVk)ZdLR7d@#wF<b>(Nczjg$^*>ooQW4kl(tmNM;^@}E>eY#mJ?T=k4{?Pkqk2xty*45LQ@bx37;cJoJ@Xg9&q<&(a%wvryCvl$@3--bvSBUvGGDBrN?|i)n{c>F2g!=|;MEi}b3%gOjS(dDi-_DEQ&4jNv3cVzLTlP0ueEl(evsHiDe?9#rPqj!{w~arLJRUE0%6dMB`ug$)n0ND!WbvzHe}eq=5--B<Vi&(+{3ThpcQFqopWfa9f65umqh2-;`OTEM;`{d4g*+7lWjzLaY=>XV8F{rzi{;$f_ro@{^V9V*&eIQVhYr3keo}j>e{qSd=b3@x@2&ygs9HhtR2sJx`7d^Hz+dPr^D=7gX3YD#cxh+$sL!$9J-s#|Pu8olPY=C^``fO+*og6T-FyZ0&R)WP)tjWQL;bi1GG4Elm`7t$IDD<FlkC$rhh%-Zr4~t^B&<)H{hFLZ=XCg{bK*C+KB<M|%QjacPot0>xZkyCjJK`YJn>WRV?F6vMd+8!sXcrn<0O2uZ=RfsgX@c5&<yL?7#M<nJAV18Q0Cot5&U05Wc+>`DgKfZIA`@@cbTu#9SWttCnSGbe;MZ|?})$StelV8<?y{x@Vf(k^`B)tXJ3%<$-cS*{+I^X7e@DNna477;A>|O9FYB%g#Bu}KT`Y$ZgLLHh?M8Uo_PiE&v|1%+s>upoYWi!d?RzW%x|YOnfGf>`56D5$+Ay-?w0krC1M%;S<hsCJM_RgV2-Z=Uwht7+Sfpyr$%^Op7ggjd|T>0Ip_RdEQRk^<|_P|eXuWVA59j2#}&En-yX<5_4Z$a{Am%Af7Mz!-}Wud#d<iNE&XlfEzgT;eHJ3my<B;|gtV6D@TIo!wSJj0PoZwouG};8Q9mjY<E-5nf_(boXz_~|OZ|?|WF7~E<>0<^?#Z}3uw%ZoMYS`LKX<0&InoPx9FbQuFm6FD<^0;U0_wOI0N;2VB=bA?I(+-7_UZ5+7D?VyuIR6JbzU0on|njfqgU^XF58fb{P_zcZ^(FzvvKG06!^|D*hh}r!?8}Z{4Dt9ck?BG@kGhL=-@E4KO|}et}mJ@eo6itXwTh#I1lxjPh}o%|1k*KM0_oHJKCci>oOSq?A%e#+s!%RKmT|n^wuM+KRq)?p39j7C&TwIi+yc7`m?;pMQuuzeJ10mwQVZxG4`Y(e{Lr^cVZq&f1mBmfa>++JZ!yR)?wR>Ox*9Cu~_FepQhNaTAd$qpw$M*x!KOdzSc_`=feNXTAai75MA2SDko3+zgqG?E{pTVY%ww)dd!agI-dM4?<une$$5IUtMu1)Oy=wAG5Ff-dK*yA2*f<-`}-8a_m=uvcX{60{g$spJ)hs?IosP^*4<w{R-s-@KJIID4w7}cxlIv#k95qtHtC^^zsFqoW_Y5EXVGREpBJ~`8_vUJ-OpYv=RgIwwW#;KtXFeHI~o5~Tj1+&#7Ulkc3BTG_14L{YlrjA+#ZPcM*Sxz^iy*^EzkFs4(xY*{D<PF_Qv~?9zIg?c^;Q>xo`#jb%ZuVKBM~cjnGO}WgN<f%KCW}wFO!*3FB_7aYx4CLb~_?&oO`ckPw`In%BEqp~K`kp*=k*^RhwPhVq?oS?7)G$@A`ZNBG8r8FKC%xhd!Et@%>lbCRrw;SutFYY+Gs{>Kv}&vzp+ekDO$;Tyf^-+T+#*&nvS`qLK9koW#uaaf=B4hzKJ|6mXF&=Q%KW^SLzdblU+YJ3XXU(zcJzIpeFyw5CnEboVP*UNiJoIm!7qrgMvr{ZPF)8#PQV>_QD&&eBqlltw)OFzTbV?0Z8c3{05+iizsKRuM^^4``v;V1qf>*Uuxa;`4jA%0EqwO=PmJ8PYRZ+c#n=Um<H@|^nONBG+1Ir2QZXUe>MQ*)Q>?_^m&Wv9ygj@>H0PhGUTq{2bWv*UTXjMt4O@U>d&Wq;*3<GtT_Q+zW-)|=jYg!ma1F`l-Y-^+9O=p4K+8=gav*Nj;$`{+bJtXJ*3P?@hP@$$Q%oRd6{N7t0!n`IK@eYj<R`F+#XUEZsWx8!$9mqPI)PRM&w@Cg~$*bJ;YGci`i^Jj<LcR?|Hqi?djA8&J$aVT<<_m8{dr2f;va&8=}DgGWeSvNsTWgH$17Jpzx+0RGA<Q#o8RL;dsb){a$Bg{+5%x_I;=Q?@buS}P9Res<>>E9&jZ~I;HJ0<T+_-5V@a=s)K%KW#wFXzFG%5r`kaFy}*ekA_0iZb6@BIW*WzZ{h7Pf4C6nJ>q-G#S@H1=9XU^1In~WRv{v|LUkbr#~2aJ}BZ(f8AJCGOu!ktM!ZBit?JfHX^FjpEi`KJ}>p(|7l}%;D7a}jpi->?>}v1sWw>gp%o*n$STDXOO+RpN3cARnniAGMRP0stayXvmt410xh}otr93~f`fjupldTxcP#i&hw-ondS@B4g6;EJU@obhAFJ)QrYL*pmU|I1-mN&AziaMVhZN+da60ImuYs89m)V1Vw<Ra>NauK<Zx{_Q-UQEp;FDB2VW{_u+$5Ru@iENwVp;q*^B8D15R`G!qlNgHUvHhw)In;UNd90H|jUnfd9gG<EbuD>4BZhriNzP@&u<aS-L`Dq9IGQ|w8bTh<@A^^)ko%I~qlS>*Bln>8CifuQsYA(j@)&9iIfmn<*v*P2R=h@T&$8n8SynuVWyQT%R@{<h#r0WM{3^?eE3jP73KuJUtY~FLpcQ?n-N}8(L#PAEL&%X<w6&t075%A^<Ve<0+>rIEQ~Q(qvrcttcXD^OqdME@Y=w>LN_OS<HfkU_ko~byeaJq{Wn(*4I~q|Nk{gk0Qmd0|k}EMsIkrV<S+X<Pm0F2hiPtI)wW6~XDOSw2VvZG48H$sw7-dCIE5fblMtz&wll(S0h&qb=4mFB8iX25wVknNMhLd03FP`mC8b<9#4kP<h-zNK$n^J?wFWc0Vq1elc7FKv#(T3_p_F|nj)F^TsuNg~iLvF)5W2s5xIBGgIiJZj#q?hVvI&}^?ogBwdJe@k1+=Ab|MV(G=LG@%PuEkL7!B8APolXuQ$5Q8#W67Be#V^;-RB{SAl$uOV=A4Bx6xXBrll?h2^{8ItP-+9J7ukz_Yrr~6J2Mp5p?Z=%+5b8W#jjI6$gh)|F%<h!1IWJQ*3?*XYw|E^CV3b+fuVRBHHDnQc28p{?m(?WuEX|qU?|q9&B!`AnCeURW&47u!^p$freKERanxz#X}sS!s!k53s&cj!%dP0D$)}7JuP_u>rFJD(C3mDQCwC+-p{^k-T|r(#{)nM?krfN6dDIo;JaRsD4LP5@jJlk>oc&qGP&|X7cnU*t7iw2>SN5|DLvdxQMphpua%J+H48_$LioF?%D^fLbMRIxSE9COzDh$On7>eDgRmtw;+SHEZ+T>2uCFCU>_f8DO26Ykn<$M?n#c9+$avtX(jiGoJbs2dUIh8tt91-T^?C$cP{?+==kAVRz{g2mwz4FgLV@h9n!^-uKA2ktSWz@6Odbm2{<#V(;O|-uQQ(Z}l'

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
